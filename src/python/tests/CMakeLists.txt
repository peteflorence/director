if(NOT BUILD_TESTING)
  return()
endif()

include(python-coverage/setup.cmake)

set(python_tests_core
  testAffordancePanel.py
  testCameraControl.py
  testConsoleApp.py
  testDepthScanner.py
  testFrameSync.py
  testHeatMap.py
  testMainWindowApp.py
  testObjectModel.py
  testPackagePath.py
  testPropertiesPanel.py
  testPointSelector.py
  testPythonConsole.py
  testTaskQueue.py
  testTransformations.py
)

set(python_tests_lcm
  testDrakeVisualizer.py
  testDrakeVisualizerInterface.py
)

set(python_tests_robot_core
  testEndEffectorIk.py
  testLoadUrdf.py
  testPyDrakeIk.py
  testRobotPoseGui.py
  testRobotSystem.py
)

set(python_tests_robot_extra
  testActionSequence.py
  testAffordanceItems.py
  testAtlasDriver.py
  testCameraView.py
  testContinuousWalking.py
  testDrawRobotLog.py
  testImageView.py
  testOtdfParser.py
  testPlanConstraints.py
  testPlaneSegmentation.py
  testTableFit.py
  testTableFitStereo.py
  testTeleopPanel.py
  testValveFit.py
  testValveFitStereo.py
  testAmazonPod.py
)

set(python_tests_standalone
)


# todo
# need this special case until robotlocomotion/lcmtypes are added to openhumanoids
if(NOT USE_DRC)
  list(APPEND python_tests_lcm testTreeViewerInterface.py)
  list(APPEND python_tests_lcm testTreeViewerClient.py)
  list(APPEND python_tests_lcm testTreeViewerPolyLine.py)
endif()


# Tests are run by default on the default robot
#
# If intending to test on a particular robot only, please set _extra_args to the
# director argument for that robot.
#
# Tests can also be run on multiple robots by setting an additional
# _extra_args_{n} to the director argument for the n-th robot to test, n >= 2.


# these tests use both Atlas v5 and Valkyrie
set(testTeleopPanel_extra_args_2 -v5)
set(testContinuousWalking_extra_args_2 -v5)

if (USE_DRC)
  set(testEndEffectorIk_extra_args --director_config ${CMAKE_SOURCE_DIR}/../models/IRB140/director_config.json)
  set(testEndEffectorIk_extra_args_2 -v5)
endif()


set(python_test_args
  --testing --data-dir ${CMAKE_SOURCE_DIR}/../../../drc-testing-data --output-dir ${CMAKE_BINARY_DIR}/Testing/Temporary
)


# for openhumanoids there is a default config but for drake there
# is not, so we'll set the default config here
if (USE_DRAKE AND NOT USE_DRC)
  list(APPEND python_test_args --iiwa-drake)
endif()


set(python_exe ${CMAKE_INSTALL_PREFIX}/bin/directorPython)

set(wrap_vfb)
if(NOT APPLE AND NOT WIN32 AND NOT DEFINED ENV{DISPLAY})
  find_program(xvfb-run xvfb-run)
  if(xvfb-run)
    set(wrap_vfb ${xvfb-run} -a -s "-screen 0 1024x768x24")
  endif()
endif()

macro(add_python_test name label)
  get_filename_component(base_name ${name} NAME_WE)
  set(test_name test_${base_name})
  add_test(${test_name} ${wrap_vfb} ${python_exe} ${CMAKE_CURRENT_SOURCE_DIR}/${name} ${python_test_args} ${${base_name}_extra_args})
  set_property(TEST ${test_name} PROPERTY ENVIRONMENT ${python_coverage_environment_arg})
  set_property(TEST ${test_name} PROPERTY LABELS ${label})
  if(wrap_vfb)
    # xvfb-run can fail to bind a display address when run in parallel
    set_property(TEST ${test_name} PROPERTY RESOURCE_LOCK xvfb)
  endif()

  # Check whether additional test cases have been defined
  set(n 2)
  while(DEFINED ${base_name}_extra_args_${n})
    set(test_name test_${base_name}_${n})
    add_test(${test_name} ${wrap_vfb} ${python_exe} ${CMAKE_CURRENT_SOURCE_DIR}/${name} ${python_test_args} ${${base_name}_extra_args_${n}})
    set_property(TEST ${test_name} PROPERTY ENVIRONMENT ${python_coverage_environment_arg})
    set_property(TEST ${test_name} PROPERTY LABELS ${label})
    if(wrap_vfb)
      # xvfb-run can fail to bind a display address when run in parallel
      set_property(TEST ${test_name} PROPERTY RESOURCE_LOCK xvfb)
    endif()
    math(EXPR n "${n}+1")
  endwhile()
endmacro()

foreach(name ${python_tests_core})
  add_python_test(${name} core)
endforeach()

if(USE_LCM)
  foreach(name ${python_tests_lcm})
    add_python_test(${name} lcm)
  endforeach()
endif()

if(USE_DRAKE)
  foreach(name ${python_tests_robot_core})
    add_python_test(${name} robot_core)
  endforeach()
endif()

if(USE_DRC)
  foreach(name ${python_tests_robot_extra})
    add_python_test(${name} robot_extra)
  endforeach()
endif()

