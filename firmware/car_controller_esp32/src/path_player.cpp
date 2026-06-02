#include "path_player.h"

bool PathPlayer::start(const PathPoint* pathPoints, size_t pointCount,
                       unsigned long nowMs) {
  if (pathPoints == nullptr || pointCount == 0) {
    return false;
  }

  pathPoints_ = pathPoints;
  pointCount_ = pointCount;
  nextPointIndex_ = 0;
  running_ = true;
  playbackStartMs_ = nowMs;
  return true;
}

void PathPlayer::stop() {
  running_ = false;
  nextPointIndex_ = 0;
}

PathPlaybackStep PathPlayer::update(unsigned long nowMs) {
  PathPlaybackStep playbackStep;

  if (!running_ || pathPoints_ == nullptr || pointCount_ == 0) {
    return playbackStep;
  }

  const unsigned long elapsedPlaybackMs = nowMs - playbackStartMs_;

  while (nextPointIndex_ < pointCount_ &&
         pathPoints_[nextPointIndex_].timestampMs <= elapsedPlaybackMs) {
    playbackStep.pathPoint = pathPoints_[nextPointIndex_];
    playbackStep.hasPointToApply = true;
    nextPointIndex_++;
  }

  if (nextPointIndex_ >= pointCount_) {
    running_ = false;
    playbackStep.completed = true;
  }

  return playbackStep;
}

bool PathPlayer::isRunning() const {
  return running_;
}
