#pragma once

#include <Arduino.h>
#include "car_types.h"

enum class PathRecordResult {
  NotDue,
  Recorded,
  Full
};

class PathRecorder {
 public:
  void start(unsigned long nowMs);
  size_t stop();
  void clear();
  PathRecordResult recordIfDue(unsigned long nowMs, const PathPoint& pathPoint);

  bool isRecording() const;
  bool hasPath() const;
  bool isFull() const;
  size_t pointCount() const;
  const PathPoint* pathPoints() const;

 private:
  PathPoint pathPoints_[MAX_RECORDED_PATH_POINTS];
  size_t pointCount_ = 0;
  bool recording_ = false;
  unsigned long recordingStartMs_ = 0;
  unsigned long lastRecordMs_ = 0;
};
