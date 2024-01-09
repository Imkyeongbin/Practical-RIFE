import gradio as gr
import cv2
import subprocess
import sys, os


def get_fps(video_path):
    """Get the frames per second of a video using OpenCV."""
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    video.release()
    return fps

def nearest_even_number_greater_than(val):
    """Find the nearest even number greater than a given value."""
    return int(val) + 1 if int(val) % 2 == 1 else int(val) + 2


def video_frame_interpolation(video_paths, target_fps, scale, output_dir):
  """Performs video frame interpolation using the given parameters.

  Args:
    video_path: Path to the input video.
    multi: The interpolation factor.
    scale: The scaling factor.
    fps: The desired output frame rate.

  Returns:
    The interpolated video.
  """
  

  script_path = os.path.dirname(os.path.abspath(__file__))
  default_path = os.path.join(script_path, 'outputs')

  # 절대 경로인 경우 그대로 사용, 상대 경로인 경우 현재 스크립트 경로에 추가
  path = default_path if output_dir is None else output_dir if os.path.isabs(output_dir) else os.path.join(script_path, output_dir)

  os.makedirs(path, exist_ok=True)

  for i in video_paths:
    video_fps = get_fps(i.name)
    desired_factor = target_fps / video_fps
    interpolation_factor = nearest_even_number_greater_than(desired_factor)
    
    filename_with_extension = os.path.basename(i.name)
    
    filename, ext = os.path.splitext(filename_with_extension)
    video_path_wo_ext = os.path.join(path, filename)
    
    vid_out_name = '{}_{}X_{}fps.{}'.format(video_path_wo_ext, interpolation_factor, int(round(desired_factor)), ext)
    
    command = [
      sys.executable, "inference_video.py",
      "--multi={}".format(interpolation_factor),
      "--video={}".format(i.name),
      f'--output="{vid_out_name}"'
    ]

    if scale != 0:
      command.extend(["--scale={}".format(scale)])
 
    
    output = subprocess.run(command)
    

  return output

demo = gr.Interface(
  fn=video_frame_interpolation,
  inputs=[
    gr.Files(label="Video"),
    gr.Slider(label="target fps(above)", value=144, minimum=0, maximum=600, step=1),
    gr.Slider(label="Scaling Factor", minimum=0, maximum=2.0, step=0.1),
    gr.Textbox(label="Output Directory (supports both abs/rel paths, default : outputs)", placeholder="Enter output directory path here")  # 출력 디렉토리 경로 입력
  ],
  outputs=[
    gr.Textbox(),
  ],
)

demo.launch(server_name="Inference_vedio simple Web UI")

@demo.gradio_function
def process(video_path, multi, scale, fps):
  return video_frame_interpolation(video_path, multi, scale, fps)

