import Flappybird, BottleJump, Game2048, PlaneWar
import interact

def create_env(Env_name):
    if Env_name == 'Flappybird':
        env = Flappybird.FlappybirdEnv()
    if Env_name == 'BottleJump':
        env = BottleJump.BottleJumpEnv()
    if Env_name == 'Game2048':
        env = Game2048.Game2048Env()
    if Env_name == 'PlaneWar':
        env = PlaneWar.PlaneWarEnv()
    return env

if __name__ == '__main__':
    env = create_env(Env_name='Flappybird')