# AutoChessPlaybackToVideo.py

import json
import argparse
from AutoChessPlayer import AutoChessPlayer
from moviepy.editor import ImageSequenceClip
import numpy as np
import os
import pygame


class AutoChessPlaybackToVideo(AutoChessPlayer):
    def __init__(self, battle_log_path, config_path=None, screen_size=(800, 800), offset=(80, 80), canvas_dimensions=(670, 670)):
        super().__init__(battle_log_path, screen_size, offset, canvas_dimensions, output_image=True, render=True)
        if config_path:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {}
        self.frame_directory = self.config.get('frame_directory', 'frames')
        self.frame_rate = self.config.get('frame_rate', 20)
        self.video_file = self.config.get('video_file', 'output.mp4')
        self.frames = [] # List to store frames in memory


    # AutoChessPlaybackToVideo.py
    def run(self):
        # Run the game as usual, which will now save frames due to the output_image flag
        super().run()

        # After the game has run, create a video from the captured frames
        # Convert PIL images to NumPy arrays
        self.frames = [np.array(frame) for frame in self.frames]

        clip = ImageSequenceClip(self.frames, fps=self.frame_rate)
        clip.write_videofile(self.video_file)

def main():
    parser = argparse.ArgumentParser(description='Generate a video from an AutoChess replay.')
    parser.add_argument('battle_log_path', type=str, help='Path to the JSON file containing the game replay.')
    parser.add_argument('config_path', type=str, nargs='?', help='Path to the configuration file.')
    parser.add_argument('-o', '--output', type=str, help='Output video file name.')

    args = parser.parse_args()


    player = AutoChessPlaybackToVideo(args.battle_log_path, args.config_path)

    # If no output file name is provided, use the base name of the .json file with .mp4 extension
    if not args.output:
        base_name = os.path.splitext(os.path.basename(args.battle_log_path))[0]
        player.video_file = os.path.join('playbacks', f"v_{base_name}.mp4")
    else:
        # If an output file name is provided, ensure it's saved in the playbacks folder
        player.video_file = os.path.join('playbacks', args.output)

    player.run()

if __name__ == "__main__":
    main()