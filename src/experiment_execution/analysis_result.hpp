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

#ifndef EXPERIMENT_EXECUTION__ANALYSIS_RESULT_HPP_
#define EXPERIMENT_EXECUTION__ANALYSIS_RESULT_HPP_

#if !defined(WIN32)
#include <sys/time.h>
#include <sys/resource.h>
#endif  // !defined(WIN32)

#include <chrono>
#include <sstream>
#include <string>

#include "../utilities/statistics_tracker.hpp"
#include "../utilities/cpu_usage_tracker.hpp"

namespace performance_test
{

#if !defined(WIN32)
/// Outstream operator for timeval to seconds (double).
std::ostream & operator<<(std::ostream & stream, const timeval & e);
#endif  // !defined(WIN32)

class AnalysisResult
{
public:
  /**
   * \brief Constructs an result with the specified parameters.
   * \param experiment_start Time the experiment started.
   * \param loop_start  Time the loop iteration started.
   * \param num_samples_received Number of samples received during the experiment iteration.
   * \param num_samples_sent Number of samples sent during the experiment iteration.
   * \param num_samples_lost Number of samples lost during the experiment iteration.
   * \param total_data_received Total data received during the experiment iteration in bytes.
   * \param latency Latency statistics of samples received.
   * \param pub_loop_time_reserve Loop time statistics of the publisher threads.
   * \param sub_loop_time_reserve Loop time statistics of the subscriber threads.
   */
  AnalysisResult(
    const std::chrono::nanoseconds experiment_start,
    const std::chrono::nanoseconds loop_start,
    const uint64_t num_samples_received,
    const uint64_t num_samples_sent,
    const uint64_t num_samples_lost,
    const std::size_t total_data_received,
    StatisticsTracker latency,
    StatisticsTracker pub_loop_time_reserve,
    StatisticsTracker sub_loop_time_reserve,
    const CpuInfo cpu_info
  );
  /**
   * \brief Returns a header for a CVS file containing the analysis result data
   * as a string. \param pretty_print If set, inserts additional tabs to format
   * the output nicer. \param st The data seperator. \return A string containing
   * the CVS header.
   */
  static std::string csv_header(const bool pretty_print = false, std::string st = ",");

  /**
   * \brief Returns the data contained the analysis result as a string.
   * \param pretty_print If set, inserts additional tabs to format the output
   * nicer. \param st The data seperator. \return A string with the contained
   * data as CSV row.
   */
  std::string to_csv_string(const bool pretty_print = false, std::string st = ",") const;

  const std::chrono::nanoseconds m_experiment_start = {};
  const std::chrono::nanoseconds m_loop_start = {};
  const uint64_t m_num_samples_received = {};
  const uint64_t m_num_samples_sent = {};
  const uint64_t m_num_samples_lost = {};
  const std::size_t m_total_data_received = {};

  StatisticsTracker m_latency;
  StatisticsTracker m_pub_loop_time_reserve;
  StatisticsTracker m_sub_loop_time_reserve;
#if !defined(WIN32)
  rusage m_sys_usage;
#endif  // !defined(WIN32)
  const CpuInfo m_cpu_info;
};

}  // namespace performance_test

#endif  // EXPERIMENT_EXECUTION__ANALYSIS_RESULT_HPP_
