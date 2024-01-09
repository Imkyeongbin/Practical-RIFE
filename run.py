import gradio as gr
import cv2
import subprocess, signal
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

# ffmpeg 옵션을 사용하는 게 아닌 거 같지만 혹시 모르니 남겨둠.
# def video_frame_interpolation(video_paths, target_fps, scale, codec, h264_crf, h264_nvenc_cq, output_dir):
def video_frame_interpolation(video_paths, target_fps, scale, output_dir):
  """Performs video frame interpolation using the given parameters.

  Args:
    video_paths: Path to the input video.
    target_fps: The interpolation factor.
    scale: The scaling factor.
    output_dir: The directory which the generated videos will be saved

  Returns:
    Completion message
  """
  

  script_path = os.path.dirname(os.path.abspath(__file__))
  default_path = os.path.join(script_path, 'outputs')

  # 절대 경로인 경우 그대로 사용, 상대 경로인 경우 현재 스크립트 경로에 추가
  path = default_path if not output_dir else output_dir if os.path.isabs(output_dir) else os.path.join(script_path, output_dir)

  os.makedirs(path, exist_ok=True)
  
  for i in video_paths:
    video_fps = get_fps(i.name)
    desired_factor = target_fps / video_fps
    interpolation_factor = nearest_even_number_greater_than(desired_factor)
    expectation_fps = video_fps * interpolation_factor
    
    filename_with_extension = os.path.basename(i.name)
    
    filename, ext = os.path.splitext(filename_with_extension)
    video_path_wo_ext = os.path.join(path, filename)
    
    vid_out_name = '{}_{}X_{}fps{}'.format(video_path_wo_ext, interpolation_factor, int(round(expectation_fps)), ext)
    
    command = [
      sys.executable, "inference_video.py",
      "--multi={}".format(interpolation_factor),
      "--video={}".format(i.name),
      f'--output={vid_out_name}'
    ]

    if scale != 0:
      command.extend(["--scale={}".format(scale)])
    
    
    # if codec == "libx264":
    #   command.extend(["-c:v libx264", "-crf", str(h264_crf)])
    # elif codec == "h264_nvenc":
    #   command.extend(["-c:v h264_nvenc", "-cq", str(h264_nvenc_cq)])
      
 
    try:
      process = subprocess.Popen(command)

      # 프로세스가 완료될 때까지 기다림
      process.wait()

    except KeyboardInterrupt:
      print("Ctrl+C가 감지되었습니다. 서브프로세스를 종료합니다.")
      if os.name == 'nt':  # Windows 경우
        process.send_signal(signal.CTRL_C_EVENT)
      else:
        process.terminate()
      sys.exit(1)
      

  return "Interpolation completed for all videos."

# nvenc_presets = [
#   "default", "slow", "medium", "fast", "hp", "hq", "bd", "ll", 
#   "llhq", "llhp", "lossless", "losslesshp", "p1", "p2", "p3", 
#   "p4", "p5", "p6", "p7"
# ]

# codecs = [
#   ('h.264','libx264'),
#   ('h.264 nvenc', 'h264_nvenc'),
# ]

# video_paths, target_fps, scale, codec, h264_crf, h264_nvenc_cq, output_dir
with gr.Blocks(title='RIFE Simple Web UI') as demo:
    gr.Markdown("## RIFE Simple Web UI")
    video_paths = gr.Files(label="Video")
    with gr.Row():
        target_fps = gr.Slider(label="target fps(above)", value=144, minimum=0, maximum=600, step=1)
        scale = gr.Slider(label="Scaling Factor", minimum=0, maximum=2.0, step=0.1)

    # with gr.Row():
    #     codec = gr.Dropdown(label="Choose Encoding codec", choices=codecs, value=codecs[0][1])
    #     with gr.Column(variant='panel'):
    #         gr.Markdown("### Adjust target quality according to the codec you chose.")
    #         with gr.Row():
    #           with gr.Column():
    #             gr.Markdown("**h.264**\n\n(crf, -12 to 51, lower is better but bigger, -1 is default)")
    #             h264_crf = gr.Slider(value=-1, minimum=-12, maximum=51, step=0.1)
    #           with gr.Column():
    #             gr.Markdown("**h.264 nvenc**\n\n(cq, 0 to 51, lower is better but bigger, 0 means automatic)")
    #             h264_nvenc_cq = gr.Slider(value=0, minimum=0, maximum=51, step=0.1)

    output_dir = gr.Textbox(label="Output Directory (supports both abs/rel paths, default : outputs)", placeholder="Enter output directory path here")
  
    submit_button = gr.Button("Generate")
    # ffmpeg쓰는 줄 알았는데 안 쓰는듯? 일단 남겨둠.
    # inputs = [video_paths, target_fps, scale, codec, h264_crf, h264_nvenc_cq, output_dir] 
    inputs = [video_paths, target_fps, scale, output_dir]
    outputs = gr.Textbox()
    
    submit_button.click(fn=video_frame_interpolation, inputs=inputs, outputs=outputs)

demo.launch()

