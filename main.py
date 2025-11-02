from utils import read_video, save_video
from trackers import PlayerTracker, BallTracker
from drawers import (
    PlayerTracksDrawer,
    BallTracksDrawer,
    TeamBallControlDrawer,
    PassInterceptionDrawer,
    CourtKeypointDrawer,
    TacticalViewDrawer,
    SpeedAndDistanceDrawer
)

from team_assigner import (
    TeamAssigner
)

from ball_acquisition import (
    BallAcquisitionDetector
)

from pass_and_interception_detector import (
    PassAndInterceptionDetector
)

from court_keypoint_detector import (
    CourtKeypointDetector
)

from tactical_view_converter import (
    TacticalViewConverter
)

from speed_and_distance_calculator import (
    SpeedAndDistanceCalculator
)

from config import (
    get_config
)
import argparse

def main(video_name):
    
    # Get configuration for the video
    config = get_config(video_name)
    
    #Read video
    video_frames = read_video(config['input_video_path'])

    #initialize tracker
    player_tracker = PlayerTracker(config['player_detector_model'])
    ball_tracker = BallTracker(config['ball_detector_model'])

    #Detect court keypoints
    court_keypoints_detector = CourtKeypointDetector(config['keypoint_detector_model'])

    #run trackers
    player_tracks = player_tracker.get_object_tracks(video_frames,
                                                     read_from_stub=config['read_from_stub'],
                                                     stub_path=config['player_track_stub']
                                                    )
    
    ball_tracks = ball_tracker.get_object_tracks(video_frames,
                                                 read_from_stub=config['read_from_stub'],
                                                 stub_path=config['ball_track_stub']
                                                 )
    
    #Get Court Keypoints
    court_keypoints = court_keypoints_detector.get_court_keypoints(video_frames,
                                                                   read_from_stub=config['read_from_stub'],
                                                                   stub_path=config['court_keypoint_stub']
                                                                   )
    
    
    #remove wrong detections
    ball_tracks = ball_tracker.remove_wrong_detections(ball_tracks)
    #interpolate missing ball tracks
    ball_tracks = ball_tracker.interpolate_ball_positions(ball_tracks)


    #Assign team to players
    team_assigner = TeamAssigner()
    player_assignment = team_assigner.get_player_teams_across_frames(video_frames,
                                                                     player_tracks,
                                                                     read_from_stub=config['read_from_stub'],
                                                                     stub_path=config['player_assignment_stub']
                                                                    )
    
    #Ball Acquisition Detection
    ball_acquisition_detector = BallAcquisitionDetector()
    ball_acquisition = ball_acquisition_detector.detect_ball_possession(player_tracks, ball_tracks)


    #Detect Passes and Interceptions
    pass_and_intercept_detector = PassAndInterceptionDetector()
    passes = pass_and_intercept_detector.detect_passes(ball_acquisition, player_assignment)
    interceptions = pass_and_intercept_detector.detect_interceptions(ball_acquisition, player_assignment)


    #Tactical View 
    tactical_view_converter = TacticalViewConverter(court_image_path=config['court_image_path'])

    court_keypoints = tactical_view_converter.validate_keypoints(court_keypoints)
    tactical_player_positions = tactical_view_converter.transform_players_to_tactical_view(court_keypoints, player_tracks)


    # Speed and Distance Calculator
    speed_and_distance_calculator = SpeedAndDistanceCalculator(
        tactical_view_converter.width,
        tactical_view_converter.height,
        tactical_view_converter.actual_width_in_meters,
        tactical_view_converter.actual_height_in_meters
    )
    player_distances_per_frame = speed_and_distance_calculator.calculate_distance(tactical_player_positions)
    player_speed_per_frame = speed_and_distance_calculator.calculate_speed(player_distances_per_frame)


    # Draw output   
    # Initialize Drawers
    player_tracks_drawer = PlayerTracksDrawer()
    ball_tracks_drawer = BallTracksDrawer()
    team_ball_control_drawer = TeamBallControlDrawer()
    pass_and_interception_drawer = PassInterceptionDrawer()
    court_keypoints_drawer = CourtKeypointDrawer()
    tactical_view_drawer = TacticalViewDrawer()
    speed_and_distance_drawer = SpeedAndDistanceDrawer()


    # Draw object Tracks
    output_video_frames = video_frames.copy()
    output_video_frames = player_tracks_drawer.draw(output_video_frames, 
                                                  player_tracks,
                                                  player_assignment,
                                                  ball_acquisition)
    output_video_frames = ball_tracks_drawer.draw(output_video_frames,
                                                 ball_tracks)


    #Team Ball Control Statistics 
    output_video_frames = team_ball_control_drawer.draw(output_video_frames,
                                                        player_assignment,
                                                        ball_acquisition)
    
    #Draw Pass and Interceptions
    output_video_frames = pass_and_interception_drawer.draw(output_video_frames,
                                                            passes,
                                                            interceptions)
    
    #Draw Court Keypoints
    output_video_frames = court_keypoints_drawer.draw(output_video_frames, 
                                                      court_keypoints)
    
    ## Draw Tactical View
    output_video_frames = tactical_view_drawer.draw(output_video_frames,
                                                    tactical_view_converter.court_image_path,
                                                    tactical_view_converter.width,
                                                    tactical_view_converter.height,
                                                    tactical_view_converter.key_points,
                                                    tactical_player_positions,
                                                    player_assignment,
                                                    ball_acquisition,
                                                    )
    

    #Draw speed and distance
    output_video_frames = speed_and_distance_drawer.draw(output_video_frames,
                                                         player_tracks,
                                                         player_distances_per_frame,
                                                         player_speed_per_frame)
    
    #save video
    save_video(output_video_frames, config['output_video_path'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Basketball video analysis')
    parser.add_argument('video_name', type=str, help='Name of the video to process (e.g., video_1, video_2)')
    parser.add_argument('--no-stub', action='store_true', help='Force reprocessing without using cached stubs')
    args = parser.parse_args()
    main(args.video_name)