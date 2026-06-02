#pragma once

#include <Arduino.h>
#include "car_types.h"

struct PathPlaybackStep {
  bool hasPointToApply = false;
  bool completed = false;
  PathPoint pathPoint;
};

class PathPlayer {
 public:
  bool start(const PathPoint* pathPoints, size_t pointCount,
             unsigned long nowMs);
  void stop();
  PathPlaybackStep update(unsigned long nowMs);
  bool isRunning() const;

 private:
  const PathPoint* pathPoints_ = nullptr;
  size_t pointCount_ = 0;
  size_t nextPointIndex_ = 0;
  bool running_ = false;
  unsigned long playbackStartMs_ = 0;
};
