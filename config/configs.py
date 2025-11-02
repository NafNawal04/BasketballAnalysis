import os

def get_config(video_name):
    # Input/Output Paths
    input_video_path = f"input_videos/{video_name}.mp4"
    output_video_path = f"output_videos/{video_name}_output.avi"
    
    # Model Paths
    player_detector_model = "models/player_detector.pt"
    ball_detector_model = "models/ball_detector.pt"
    keypoint_detector_model = "models/keypoint_detector.pt"
    
    # Court Image Path
    court_image_path = "./images/basketball_court.png"
    
    # Stub Configuration
    stub_dir = f"stubs/{video_name}"
    os.makedirs(stub_dir, exist_ok=True)
    
    # Stub Paths
    player_track_stub = f"{stub_dir}/player_track_stubs.pkl"
    ball_track_stub = f"{stub_dir}/ball_track_stubs.pkl"
    court_keypoint_stub = f"{stub_dir}/court_keypoint_stubs.pkl"
    player_assignment_stub = f"{stub_dir}/player_assignment_stub.pkl"

    read_from_stub = True  
    
    return {
        'video_name': video_name,
        'input_video_path': input_video_path,
        'output_video_path': output_video_path,
        'player_detector_model': player_detector_model,
        'ball_detector_model': ball_detector_model,
        'keypoint_detector_model': keypoint_detector_model,
        'court_image_path': court_image_path,
        'player_track_stub': player_track_stub,
        'ball_track_stub': ball_track_stub,
        'court_keypoint_stub': court_keypoint_stub,
        'player_assignment_stub': player_assignment_stub,
        'read_from_stub': read_from_stub
    }