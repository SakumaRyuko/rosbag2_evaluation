// Copyright 2017 Apex.AI, Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#ifndef UTILITIES__RT_ENABLER_HPP_
#define UTILITIES__RT_ENABLER_HPP_

#include <sys/mman.h>
#include <malloc.h>
#include <unistd.h>
#include <sched.h>
#include <sys/types.h>
#if defined(PERFORMANCE_TEST_LINUX)
#include <sys/syscall.h>
#elif defined(QNX)
#include <sys/neutrino.h>
#include <sys/syspage.h>
#endif  // defined(PERFORMANCE_TEST_LINUX)

#include <iostream>
#include <cerrno>
#include <cstring>
#include <memory>

namespace performance_test
{

///
/// An estimate of physical memory the process might use
/// NOTE: This is just a rough estimate for the lidar_detector process
///
static const uint64_t PROCESS_MAX_DYN_MEM = (2U * 1024U * 1024U * 1024U);  // 2GB

/// \brief Real time related info for the process
typedef struct proc_rt_info_s
{
  /// Flag if RT is enabled or not for the process
  bool is_rt;
  /// Default cpu bit mask of all the threads
  uint32_t proc_cpu_bit_mask;
  /// Default proc priority for the tasks
  int32_t proc_prio;
} proc_rt_info_type_t;

/// Global variable holding real time information.
static proc_rt_info_type_t proc_rt_info;

///
/// \brief Check if the process is set with RT parameters or not
/// \return true is RT params are set, if not false
inline bool proc_is_rt()
{
  return proc_rt_info.is_rt;
}

///
/// Mem related post initialization to increase determinism and
/// thereby reduce latency for the entire process
/// NOTE: This is is still very raw and under development
///
/// \brief Perform some RT related memory process initialization
/// \return 0 on success, throw an exception on error
inline void post_proc_rt_init()
{
  int32_t res = 0;

  // void * buf = nullptr;
  const int64_t pg_sz = sysconf(_SC_PAGESIZE);


  if (pg_sz <= 0) {
    std::cerr << "proc rt init getting system page size failed" << \
      strerror(errno) << std::endl;
    throw std::runtime_error("proc rt init getting system page size faile");
  }
  // FIX IT: proc_rt_info.is_rt is false even after pre_proc_rt_init()
  //
  // Lock the current memory in RAM.
  // Based on various QoS settings, certain middleware implementaions, allocates excessive
  // virtual memory dynamically. Locking this excessive virtual memory into physical memory will
  // cause running out of physical memory. Therefore, MCL_FUTURE option is disabled.
  //
  res = mlockall(MCL_CURRENT);
  if (res < 0) {
    std::cerr << "proc rt init mem locking failed" << strerror(errno) << std::endl;
    throw std::runtime_error("proc rt init mem locking failed");
  }
#ifdef PERFORMANCE_TEST_LINUX
  //
  // Disable all the heap trimming operation using the following option.
  // This avoid releasing of free mem back to the system
  //
  res = mallopt(M_TRIM_THRESHOLD, -1);
  if (res <= 0) {
    std::cerr << "proc rt init trim threshold failed" << strerror(errno) << std::endl;
    throw std::runtime_error("proc rt init trim threshold failed");
  }
  //
  // Disable mmap(). Because, memory allocated by mmap is outside the heap region
  // and when the memory is freed, it does not go back to the free list to be later
  // used by allocations. Also mmap() is an expensive task. Based on M_MAP_THRESOLD,
  // the kernel will either use mmap() or sbrk() to get the requested memory.
  // More info look at "man mallopt"
  //
  res = mallopt(M_MMAP_MAX, 0);
  if (res <= 0) {
    std::cerr << "proc rt mmap disabling failed" << strerror(errno) << std::endl;
    throw std::runtime_error("proc rt mmap disabling failed");
  }
#endif  // PERFORMANCE_TEST_LINUX
  //
  // Since all the memory is not statically allocated yet, Allocate and free
  // the memory so all pages gets mapped and locked in the process addr space
  //
//  res = posix_memalign(&buf, static_cast<size_t>(pg_sz), PROCESS_MAX_DYN_MEM);
//  if (res != 0) {
//    std::cerr << "proc rt init mem aligning failed" << strerror(errno) << std::endl;
//    throw std::runtime_error("proc rt init mem aligning failed");
//  }
//  memset(buf, 0, PROCESS_MAX_DYN_MEM);
//  free(buf);
}

///
/// CPU affinity related pre initialization to increase determinism and
/// thereby reduce latency for the entire process
/// NOTE: This is is still very raw and under development
///
/// \brief Perform some RT related process initialization
/// \param[in] cpu_bit_mask_in Default cpu affinity of all the threads in the process
/// \param[in] prio default prio of all the threads in the process
/// \return 0 on success, throw an exception on error
inline void pre_proc_rt_init(const uint32_t cpu_bit_mask_in, const int32_t prio)
{
  int32_t res = 0;

  uint32_t cpu_bit_mask = cpu_bit_mask_in;

  //
  // Set the is_rt flag if any of the proc RT params are set
  //
  proc_rt_info.is_rt = false;
  proc_rt_info.proc_cpu_bit_mask = 0U;
  proc_rt_info.proc_prio = 0;
  if ((cpu_bit_mask > 0U) || (prio > 0)) {
    proc_rt_info.is_rt = true;
    proc_rt_info.proc_cpu_bit_mask = cpu_bit_mask;
    proc_rt_info.proc_prio = prio;
  }

  if (proc_rt_info.is_rt) {
    //
    // Set prio for all the tasks of the process
    //
    if (proc_rt_info.proc_prio > 0) {
      struct sched_param param;
      memset(&param, 0, sizeof(param));
      param.sched_priority = proc_rt_info.proc_prio;
      res = sched_setscheduler(getpid(), SCHED_FIFO, &param);
      if (res < 0) {
        std::cerr << "proc rt init prio setting failed" << strerror(errno) << std::endl;
        throw std::runtime_error("proc rt init prio setting failed");
      }
    }

    //
    // Set thread-cpu affinity
    //
    if (proc_rt_info.proc_cpu_bit_mask > 0U) {
#ifdef PERFORMANCE_TEST_LINUX
      cpu_set_t set;
      uint32_t cpu_cnt = 0U;
      CPU_ZERO(&set);
      while (cpu_bit_mask > 0U) {
        if ((cpu_bit_mask & 0x1U) > 0) {
          CPU_SET(cpu_cnt, &set);
        }
        cpu_bit_mask = (cpu_bit_mask >> 1U);
        cpu_cnt++;
      }
      res = sched_setaffinity(getpid(), sizeof(set), &set);
      if (res < 0) {
        std::cerr << "proc rt init affinity setting failed" << strerror(errno) << std::endl;
        throw std::runtime_error("proc rt init affinity setting failed");
      }
#elif defined(QNX)
      uint32_t num_elements = 0u;
      int32_t * rsizep, * rmaskp, * imaskp;
      uint64_t masksize_bytes, size;
      void * my_data;

      // http://www.qnx.com/developers/docs/7.0.0/index.html#com.qnx.doc.neutrino.prog/topic/multicore_thread_affinity.html
      // Determine the number of array elements required to hold
      // the runmasks, based on the number of CPUs in the system.

      num_elements = (uint32_t)RMSK_SIZE(_syspage_ptr->num_cpu);

      // Determine the size of the runmask, in bytes.
      masksize_bytes = num_elements * sizeof(uint32_t);

      // Allocate memory for the data structure that we'll pass
      // to ThreadCtl(). We need space for an integer (the number
      // of elements in each mask array) and the two masks
      // (runmask and inherit mask).

      size = sizeof(int32_t) + 2u * masksize_bytes;
      my_data = malloc(size);
      if (NULL != my_data) {
        memset(my_data, 0x00, size);

        // Set up pointers to the "members" of the structure.
        rsizep = static_cast<int32_t *>(my_data);
        rmaskp = rsizep + 1u;
        imaskp = rmaskp + num_elements;

        // Set the size.
        *rsizep = static_cast<int32_t>(num_elements);

        // Set the runmask and inherit mask. Call this macro once for each processor
        // the thread and its children can run on.
        uint64_t cmask = cpu_bit_mask_in;
        uint32_t cpu = 0u;
        while (cmask > 0u) {
          if (cmask & 1u) {
            RMSK_SET(cpu, rmaskp);
            RMSK_SET(cpu, imaskp);
          }
          cpu++;
          cmask = (cmask >> 1u);
        }

        if (ThreadCtl(_NTO_TCTL_RUNMASK_GET_AND_SET_INHERIT, my_data) == -1) {
          std::cerr << "proc rt init set affinity failed" << strerror(errno) << std::endl;
          throw std::runtime_error("proc rt init affinity setting failed");
        }
        free(my_data);
      } else {
        std::cerr << "proc rt init affinity mem alloc failed" << strerror(errno) << std::endl;
        throw std::runtime_error("proc rt init affinity setting failed");
      }
#else
      throw std::runtime_error("proc rt init affinity setting not supported on this platform");
#endif  // PERFORMANCE_TEST_LINUX
    }
  }
}

}  // namespace performance_test


#endif  // UTILITIES__RT_ENABLER_HPP_
