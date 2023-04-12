import glob

from PIL import Image



def make_gif(frame_folder):
    # get all image files in the folder in order
    frames = []
    imgs = glob.glob(frame_folder + "/*.png")
    # sort the image name scring numerically
    imgs.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    for i in imgs:
        print(i)
        new_frame = Image.open(i)
        frames.append(new_frame)


    frame_one = frames[0]
    save_path = frame_folder + "/my_awesome.gif"
    frame_one.save(save_path, format="GIF", append_images=frames,
            save_all=True, duration=100, loop=0)
    

def recusive_gif_generation(folder_path):
    for folder in glob.glob(folder_path + "/*"):
        if "gif" in folder:
            make_gif(folder)
        else:
            recusive_gif_generation(folder)


if __name__ == "__main__":
    # make_gif("data/Frontier_Random/nbots:4_rows:20_cols:20_seed:20/2023-04-12_14:13:23/gif")
