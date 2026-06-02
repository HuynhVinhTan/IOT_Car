#include "path_recorder.h"

void PathRecorder::start(unsigned long nowMs) {
  pointCount_ = 0;
  recording_ = true;
  recordingStartMs_ = nowMs;
  lastRecordMs_ = 0;
}

size_t PathRecorder::stop() {
  recording_ = false;
  return pointCount_;
}

void PathRecorder::clear() {
  pointCount_ = 0;
  recording_ = false;
  recordingStartMs_ = 0;
  lastRecordMs_ = 0;
}

PathRecordResult PathRecorder::recordIfDue(unsigned long nowMs,
                                           const PathPoint& pathPoint) {
  if (!recording_) {
    return PathRecordResult::NotDue;
  }

  if (lastRecordMs_ != 0 && nowMs - lastRecordMs_ < PATH_RECORD_INTERVAL_MS) {
    return PathRecordResult::NotDue;
  }

  if (pointCount_ >= MAX_RECORDED_PATH_POINTS) {
    recording_ = false;
    return PathRecordResult::Full;
  }

  PathPoint recordedPathPoint = pathPoint;
  recordedPathPoint.timestampMs = nowMs - recordingStartMs_;
  pathPoints_[pointCount_] = recordedPathPoint;
  pointCount_++;
  lastRecordMs_ = nowMs;

  if (pointCount_ >= MAX_RECORDED_PATH_POINTS) {
    recording_ = false;
    return PathRecordResult::Full;
  }

  return PathRecordResult::Recorded;
}

bool PathRecorder::isRecording() const {
  return recording_;
}

bool PathRecorder::hasPath() const {
  return pointCount_ > 0;
}

bool PathRecorder::isFull() const {
  return pointCount_ >= MAX_RECORDED_PATH_POINTS;
}

size_t PathRecorder::pointCount() const {
  return pointCount_;
}

const PathPoint* PathRecorder::pathPoints() const {
  return pathPoints_;
}
