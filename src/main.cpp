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

#ifdef PERFORMANCE_TEST_RCLCPP_ENABLED
#include <rclcpp/rclcpp.hpp>
#endif

#include <memory>
#include <vector>

#include "communication_abstractions/resource_manager.hpp"
#include "experiment_configuration/experiment_configuration.hpp"
#include "experiment_execution/analyze_runner.hpp"

int main(int argc, char ** argv)
{
  // parse arguments and set up experiment configuration
  auto & ec = performance_test::ExperimentConfiguration::get();
  ec.setup(argc, argv);

#ifdef PERFORMANCE_TEST_RCLCPP_ENABLED
  // initialize ros
  if (ec.use_ros2_layers()) {
    rclcpp::init(argc, argv);
  }
#endif

  // run the experiment
  {
    performance_test::AnalyzeRunner ar;
    ar.run();
  }

  // shut down cleanly
  performance_test::ResourceManager::shutdown();
}
