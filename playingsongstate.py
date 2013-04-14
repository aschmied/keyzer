class PlayingSongState(object):

    _currentTick = 0

    @staticmethod
    def getCurrentTick():
        return PlayingSongState._currentTick

    @staticmethod
    def onTickUpdate(tick):
        PlayingSongState._currentTick = tick
