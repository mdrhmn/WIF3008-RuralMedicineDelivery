import ttkbootstrap
from PIL import Image, ImageTk
# Temporarily disable import
import ttkbootstrap as ttk
import tkinter as tki
from tkinter import *
import threading
import datetime
import platform
import time
import cv2
import os

d = '20'
a = '1'
dl = 0


class TelloUI:
    """Wrapper class to enable the GUI."""

    def __init__(self, tello, checkpoint, outputpath):
        """
        Initial all the element of the GUI,support by Tkinter

        :param tello: class interacts with the Tello drone.

        Raises: RuntimeError: If the Tello rejects the attempt to enter command mode.
        """
        # Videostream device
        self.tello = tello

        # The path that save pictures created by clicking the take_snapshot button
        self.outputPath = outputpath
        self.checkpoint = checkpoint

        # Frame read from h264decoder and used for pose recognition
        self.frame = None

        # Thread of the Tkinter mainloop
        self.thread = None
        self.stopEvent = None
        self.quit = False
        self.autoFlightToken = False
        self.current_round = 1
        self.current_checkpoint = 0
        self.isPause = False
        self.isStop = False

        # Control variables
        self.distance = 0.2  # default distance for 'move' cmd
        self.degree = 0  # default degree for 'cw' or 'ccw' cmd

        # If flag is TRUE, the auto-takeoff thread will stop waiting for the response from tello
        self.quit_waiting_flag = False

        # Initialize the root window and image panel
        self.root = tki.Tk()
        # Initialize Ttkbootstrap
        self.style = ttk.Style()
        self.panel = None

        # ---------------------------------------------------------------------------- #
        #                                   RED ZONE                                   #
        # ---------------------------------------------------------------------------- #

        # ------------------------------- Console Frame ------------------------------ #

        red_zone_1 = Frame(self.root)
        red_zone_1.pack(fill="both", expand="yes",
                        side="bottom", pady=20, padx=20)

        console_content = LabelFrame(red_zone_1, text="Console")
        console_content.pack(fill="both", expand="yes", side="top")

        scrollbar = Scrollbar(console_content)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.mylist = Listbox(
            console_content, yscrollcommand=scrollbar.set, width=200, selectmode=BROWSE)
        self.mylist.selection_set(first=0, last=None)
        self.mylist.selection_clear(2)
        self.mylist.see("end")

        self.mylist.pack(side=LEFT, fill=BOTH)
        scrollbar.config(command=self.mylist.yview)

        # -------------------------------- Video Frame ------------------------------- #

        # Create buttons
        red_zone_2 = Frame(self.root)
        red_zone_2.pack(fill="both", expand="yes",
                        side="bottom", pady=20, padx=20)

        video_frame = LabelFrame(red_zone_2, text="Video")
        video_frame.pack(fill="both", expand="yes", side="left")

        # -------------------------- Automatic Flight Frame -------------------------- #

        self.btn_snapshot = ttk.Button(video_frame, text="Take Snapshot", bootstyle='primary',
                                       command=self.take_snapshot)
        self.btn_snapshot.pack(side="bottom", fill="both",
                               expand="yes", padx=10, pady=5)

        self.btn_pause = ttk.Button(
            video_frame, bootstyle='warning', text="Pause", command=self.pause_video)
        self.btn_pause.pack(side="bottom", fill="both",
                            expand="yes", padx=10, pady=5)

        plan_frame_1 = LabelFrame(red_zone_2, text="Automatic Flight")
        plan_frame_1.pack(fill="both", expand="yes", side="right")

        plan_frame_2 = Frame(plan_frame_1)
        plan_frame_2.pack(fill="both", side="right")

        self.btn_autoFlight = ttk.Button(plan_frame_1, text="Start", bootstyle='success',
                                         command=self.auto_control_flight)
        self.btn_autoFlight.pack(side="top", fill="both",
                                 expand="yes", padx=10, pady=5)

        self.btn_autoFlight_pause = ttk.Button(plan_frame_2, text="Pause", bootstyle='warning',
                                               command=self.auto_flight_pause)
        self.btn_autoFlight_pause.pack(side="top", fill="both",
                                       expand="yes", padx=10, pady=5)

        self.btn_autoFlight_stop = ttk.Button(plan_frame_2, text="Stop", bootstyle='danger',
                                              command=self.auto_flight_stop)
        self.btn_autoFlight_stop.pack(side="top", fill="both",
                                      expand="yes", padx=10, pady=5)

        self.btn_autoFlight_stop["state"] = DISABLED
        self.btn_autoFlight_pause["state"] = DISABLED

        # ---------------------------------------------------------------------------- #
        #                                END OF RED ZONE                               #
        # ---------------------------------------------------------------------------- #

        # ---------------------------------------------------------------------------- #
        #                                   BLUE ZONE                                  #
        # ---------------------------------------------------------------------------- #

        # --------------------------------- Column 1 --------------------------------- #

        blue_zone = Frame(self.root)
        blue_zone.pack(fill="both", expand="yes", side="top", pady=20, padx=20)

        col1 = LabelFrame(blue_zone, text="Set Distance")
        col1.pack(fill="both", expand="yes", side="left")

        self.btn_distance = ttk.Button(col1, bootstyle="info", text="Set Distance",
                                       command=self.update_distance_bar)
        self.btn_distance.pack(side="bottom", fill="both",
                               expand="yes", padx=10, pady=5)

        self.distance_bar = ttkbootstrap.Meter(col1,
                                               bootstyle="info",
                                               amounttotal=500,
                                               amountused=self.distance*100,
                                               subtext='Distance',
                                               textright='cm',
                                               stripethickness=5,
                                               interactive=False)
        self.distance_bar.pack(side="top")

        self.distance_scale = ttk.Scale(
            col1,
            bootstyle="info",
            orient=HORIZONTAL,
            value=self.distance,
            from_=0,
            to=500, command=self.setDistanceMeter
        )
        self.distance_scale.pack(fill=X, padx=20, pady=5, expand=YES)
        self.distance_scale.set(self.distance*100)

        # --------------------------------- Column 2 --------------------------------- #

        col2 = LabelFrame(blue_zone, text="Second Panel")
        col2.pack(fill="both", expand="yes", side="left")

        self.btn_reset_battery = ttk.Button(col2, bootstyle='dark', text="Reset to Full Battery",
                                            command=self.reset_battery)
        self.btn_reset_battery.pack(side="top", fill="both",
                                    expand="yes", padx=10, pady=5)

        self.btn_landing = ttk.Button(
            col2, bootstyle='danger', text="Land", command=self.tello_landing)
        self.btn_landing.pack(side="bottom", fill="both",
                              expand="yes", padx=10, pady=5)

        self.btn_takeoff = ttk.Button(
            col2, bootstyle='success', text="Take Off", command=self.tello_take_off)
        self.btn_takeoff.pack(side="bottom", fill="both",
                              expand="yes", padx=10, pady=5)

        # --------------------------------- Column 3 --------------------------------- #

        col3 = LabelFrame(blue_zone, text="Set Rotation Degree")
        col3.pack(fill="both", expand="yes", side="right")

        self.degree_bar = ttkbootstrap.Meter(col3,
                                             bootstyle="info",
                                             amountused=self.degree,
                                             subtext='Degree',
                                             amounttotal=360,
                                             textright='o',
                                             stripethickness=10,
                                             interactive=True)
        self.degree_bar.pack(side="top")

        self.degree_scale = ttk.Scale(col3,
                                      bootstyle="info",
                                      from_=0, to=360,
                                      orient=HORIZONTAL,
                                      command=self.setDegreeMeter)
        self.degree_scale.set(self.degree)
        self.degree_scale.pack(fill=X, padx=20, pady=5, expand=YES)

        self.btn_degree = ttk.Button(col3, bootstyle="info", text="Set Rotation Degree",
                                     command=self.update_degree_bar)
        self.btn_degree.pack(side="bottom", fill="both",
                             expand="yes", padx=10, pady=5)

        # ---------------------------------------------------------------------------- #
        #                               END OF BLUE ZONE                               #
        # ---------------------------------------------------------------------------- #

        # ---------------------------------------------------------------------------- #
        #                                  GREEN ZONE                                  #
        # ---------------------------------------------------------------------------- #

        # ----------------------------- Instruction Frame ---------------------------- #

        green_zone_1 = LabelFrame(self.root, text="Movement")
        green_zone_1.pack(fill="both", expand="yes",
                          side="top", pady=20, padx=20)

        movement_instructions = Frame(green_zone_1)
        movement_instructions.pack(fill="both", expand="yes",
                                   side="left", padx=20)

        text1 = ttk.Label(movement_instructions, text='W - Move Tello Up\n'
                                                      'S - Move Tello Down\n'
                                                      'A - Rotate Tello Counter-Clockwise\n'
                                                      'D - Rotate Tello Clockwise\n'
                                                      'Arrow Up - Move Tello Forward\n'
                                                      'Arrow Down - Move Tello Backward\n'
                                                      'Arrow Left - Move Tello Left\n'
                                                      'Arrow Right - Move Tello Right\n',
                          justify="left")
        text1.pack(fill="both", expand="yes",
                   side="right", padx=20)

        # Binding arrow keys to drone control
        self.tmp_f = tki.Frame(self.root, width=100, height=2)
        self.tmp_f.bind('<KeyPress-w>', self.on_keypress_w)
        self.tmp_f.bind('<KeyPress-s>', self.on_keypress_s)
        self.tmp_f.bind('<KeyPress-a>', self.on_keypress_a)
        self.tmp_f.bind('<KeyPress-d>', self.on_keypress_d)
        self.tmp_f.bind('<KeyPress-Up>', self.on_keypress_up)
        self.tmp_f.bind('<KeyPress-Down>', self.on_keypress_down)
        self.tmp_f.bind('<KeyPress-Left>', self.on_keypress_left)
        self.tmp_f.bind('<KeyPress-Right>', self.on_keypress_right)
        self.tmp_f.pack(side="bottom")
        self.tmp_f.focus_set()

        # -------------------- Left/Right, Forward/Backword Frame -------------------- #

        first_btn_set = Frame(green_zone_1)
        first_btn_set.pack(fill="both", expand="yes",
                           side="left", padx=50)

        # Arrows Icon
        # upIcon = tki.PhotoImage(file=r"./icons/up-arrow.png")
        # downIcon = tki.PhotoImage(file=r"./icons/down-arrow.png")
        # leftIcon = tki.PhotoImage(file=r"./icons/left-arrow.png")
        # rightIcon = tki.PhotoImage(file=r"./icons/right-arrow.png")

        self.btn_moveleft = ttk.Button(
            first_btn_set, text="Move Left", bootstyle='secondary', command=self.tello_move_left)
            # first_btn_set, text="Move Left", bootstyle='secondary', command=self.tello.move_left(self.distance,0))
            # first_btn_set, text='Move Left', bootstyle='secondary',
            # command=lambda: [threading.Thread(target=tello.send_command, args=(f'left {d}',dl)).start(), self.append_console('Move Left')])
        self.btn_moveleft.pack(side="left")

        self.btn_moveright = ttk.Button(
            first_btn_set, text="Move Right", bootstyle='secondary', command=self.tello_move_right)
            # first_btn_set, text="Move Right", bootstyle='secondary', command=self.tello.move_right(self.distance,0))
            # first_btn_set, text='Move Right', bootstyle='secondary',
            # command=lambda: [threading.Thread(target=tello.send_command, args=(f'right {d}',dl)).start(), self.append_console('Move Right')])
        self.btn_moveright.pack(side="right")

        self.btn_moveforward = ttk.Button(
            first_btn_set, text="Move Forward", bootstyle='secondary', command=self.tello_move_forward)
            # first_btn_set, text="Move Forward", bootstyle='secondary', command=self.tello.move_forward(self.distance,0))
            # first_btn_set, text='Move Forward', bootstyle='secondary',
            # command=lambda: [threading.Thread(target=tello.send_command, args=(f'forward {d}',dl)).start(), self.append_console('Move Forward')])
        self.btn_moveforward.pack(side="top", pady=10)

        self.btn_movebackward = ttk.Button(
            first_btn_set, text="Move Backward", bootstyle='secondary', command=self.tello_move_backward)
            # first_btn_set, text="Move Backward", bootstyle='secondary', command=self.tello.move_backward(self.distance,0))
            # first_btn_set, text='Move Backward', bootstyle='secondary',
            # command=lambda: [threading.Thread(target=tello.send_command, args=(f'back {d}',dl)).start(), self.append_console('Move Backward')])
        self.btn_movebackward.pack(side="bottom", pady=10)

        # -------------------------- Rotation, Up/Down Frame ------------------------- #

        second_btn_set = Frame(green_zone_1)
        second_btn_set.pack(fill="both", expand="yes",
                            side="left", padx=50)

        self.btn_rotatecw = ttk.Button(
            second_btn_set, text="Rotate CW", bootstyle='secondary', command=self.tello_rotate_cw)
            # second_btn_set, text="Rotate CW", bootstyle='secondary', command=self.tello.rotate_cw(self.degree,0))
            # second_btn_set, text='Rotate CW', bootstyle='secondary',
            # command=lambda: [threading.Thread(target=tello.send_command, args=(f'cw {a}',dl)).start(), self.append_console('Rotate CW')])
        self.btn_rotatecw.pack(side="left")

        self.btn_rotateccw = ttk.Button(
            second_btn_set, text="Rotate CCW", bootstyle='secondary', command=self.tello_rotate_ccw)
            # second_btn_set, text="Rotate CCW", bootstyle='secondary', command=self.tello.rotate_ccw(self.degree,0))
            # second_btn_set, text='Rotate CCW', bootstyle='secondary',
            # command=lambda: [threading.Thread(target=tello.send_command, args=(f'ccw {a}',dl)).start(), self.append_console('Rotate CCW')])
        self.btn_rotateccw.pack(side="right")

        self.btn_moveup = ttk.Button(
            second_btn_set, text="Move Up", bootstyle='secondary', command=self.tello_move_up)
            # second_btn_set, text="Move Up", bootstyle='secondary', command=self.tello.move_up(20,0))
            # second_btn_set, text='Move Up', bootstyle='secondary',
            # command=lambda: [threading.Thread(target=tello.send_command, args=(f'up {a}',dl)).start(), self.append_console('Move Up')])
        self.btn_moveup.pack(side="top", pady=10)

        self.btn_movedown = ttk.Button(
            second_btn_set, text="Move Down", bootstyle='secondary', command=self.tello_move_down)
            # second_btn_set, text="Move Down", bootstyle='secondary', command=self.tello.move_down(20,0))
            # second_btn_set, text='Move Down', bootstyle='secondary',
            # command=lambda: [threading.Thread(target=tello.send_command, args=(f'down {a}',dl)).start(), self.append_console('Move Down')])
        self.btn_movedown.pack(side="bottom", pady=10)

        # -------------------------------- Flip Frame -------------------------------- #

        third_btn_set = Frame(green_zone_1)
        third_btn_set.pack(fill="both", expand="yes",
                           side="left", padx=50)

        self.btn_flipl = ttk.Button(
            third_btn_set, text="Flip Left", bootstyle='secondary', command=self.tello_flip_left)
        self.btn_flipl.pack(side="left")

        self.btn_flipr = ttk.Button(
            third_btn_set, text="Flip Right", bootstyle='secondary', command=self.tello_flip_right)
        self.btn_flipr.pack(side="right")

        self.btn_flipf = ttk.Button(
            third_btn_set, text="Flip Forward", bootstyle='secondary', command=self.tello_flip_forward)
        self.btn_flipf.pack(side="top", pady=10)

        self.btn_flipb = ttk.Button(
            third_btn_set, text="Flip Backward", bootstyle='secondary', command=self.tello_flip_backward)
        self.btn_flipb.pack(side="bottom", pady=10)

        # ---------------------------------------------------------------------------- #
        #                               END OF GREEN ZONE                              #
        # ---------------------------------------------------------------------------- #

        # ----------------------------- Control UI Logic ----------------------------- #

        # Start a thread that constantly pools the video sensor for
        # the most recently read frame
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()

        # Set a callback to handle when the window is closed
        self.root.wm_title("Tello Drone Controller")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.on_close)

        # Sending_command will send command to tello every 5 seconds
        self.sending_command_thread = threading.Thread(
            target=self._sendingCommand)
        self.loop = True

        while self.loop:
            self.root.update()

    def videoLoop(self):
        """
        The mainloop thread of Tkinter
        Raises:
        RuntimeError: To get around a RunTime error that Tkinter throws due to threading.
        """
        try:
            # Start the thread that get GUI image and drwa skeleton
            time.sleep(0.5)
            self.sending_command_thread.start()

            while not self.stopEvent.is_set():
                system = platform.system()

                # Read the frame for GUI show
                self.frame = self.tello.read()
                if self.frame is None or self.frame.size == 0:
                    continue

                # Transfer the format from frame to image
                image = Image.fromarray(self.frame)

                # We found compatibility problem between Tkinter,PIL and MacoOS, and it will
                # sometimes result to a very long preriod of the "ImageTk.PhotoImage" function,
                # so for MacOS,we start a new thread to execute the _updateGUIImage function.
                if system == "Windows" or system == "Linux":
                    self._updateGUIImage(image)

                else:
                    thread_tmp = threading.Thread(
                        target=self._updateGUIImage, args=(image,))
                    thread_tmp.start()
                    time.sleep(0.03)

        except RuntimeError as e:
            print("[INFO] Caught a RuntimeError")

    def _updateGUIImage(self, image):
        """
        Main operation to initial the object of image,and update the GUI panel
        """

        image = ImageTk.PhotoImage(image)

        # If the panel is None, we need to initialise it
        if self.panel is None:
            self.panel = tki.Label(image=image)
            self.panel.image = image
            self.panel.pack(side="left", padx=10, pady=10)
        # otherwise, simply update the panel
        else:
            self.panel.configure(image=image)
            self.panel.image = image

    def _sendingCommand(self):
        """
        Start a while loop that sends 'command' to tello every 5 second
        """

        # while True:
        #     self.tello.send_command('command',0)
        #     time.sleep(5)

    def _sendCommand(self, command):
        """
        Start a while loop that sends 'command' to tello every 5 second
        """

        self.tello.send_command(command)

    def _setQuitWaitingFlag(self):
        """
        Set the variable as TRUE, it will stop computer waiting for response from Tello
        """
        self.quit_waiting_flag = True

    def take_snapshot(self):
        """
        Save the current frame of the video as a .jpg file and put it into output path
        """

        # Grab the current timestamp and use it to construct the filename
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))

        p = os.path.sep.join((self.outputPath, filename))

        # Save the file
        cv2.imwrite(p, cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR))
        print("[INFO] saved {}".format(filename))

    def pause_video(self):
        """
        Toggle the freeze/unfreeze of video
        """

        if self.btn_pause.config('relief')[-1] == 'sunken':
            self.btn_pause.config(relief="raised")
            self.tello.video_freeze(False)
            self.append_console("False")
        else:
            self.btn_pause.config(relief="sunken")
            self.tello.video_freeze(True)
            self.append_console("True")

        # ---------------------------------------------------------------------------- #
        #                          TELLO DRONE FUNCTIONALITIES                         #
        # ---------------------------------------------------------------------------- #

    def tello_take_off(self):
        if not self.autoFlightToken:
            self.append_console("Take off")
            return self.tello.takeoff()
        else:
            self.auto_flight_pause()

    def tello_landing(self):
        if not self.autoFlightToken:
            self.append_console("Landing")
            return self.tello.land()
        else:
            self.auto_flight_pause()

    def tello_flip_left(self):
        if not self.autoFlightToken:
            self.append_console("Flip Left")
            return self.tello.flip('l', 0)
        else:
            self.auto_flight_pause()

    def tello_flip_right(self):
        if not self.autoFlightToken:
            self.append_console("Flip Right")
            return self.tello.flip('r', 0)
        else:
            self.auto_flight_pause()

    def tello_flip_forward(self):
        if not self.autoFlightToken:
            self.append_console("Flip Forward")
            return self.tello.flip('f', 0)
        else:
            self.auto_flight_pause()

    def tello_flip_backward(self):
        if not self.autoFlightToken:
            self.append_console("Flip Backward")
            return self.tello.flip('b', 0)
        else:
            self.auto_flight_pause()

    def tello_rotate_cw(self):
        if not self.autoFlightToken:
            self.append_console("Rotate clockwise")
            return self.tello.rotate_cw(self.degree, 0)
        else:
            self.auto_flight_pause()

    def tello_rotate_ccw(self):
        if not self.autoFlightToken:
            self.append_console("Rotate counter-clockwise")
            return self.tello.rotate_ccw(self.degree, 0)
        else:
            self.auto_flight_pause()

    def tello_move_forward(self):
        if not self.autoFlightToken:
            self.append_console("Moving Forward")
            print(self.distance)
            return self.tello.move_forward(self.distance, 0)
        else:
            self.auto_flight_pause()

    def tello_move_backward(self):
        if not self.autoFlightToken:
            self.append_console("Moving Backward")
            return self.tello.move_backward(self.distance, 0)
        else:
            self.auto_flight_pause()

    def tello_move_left(self):
        if not self.autoFlightToken:
            self.append_console("Moving Left")
            return self.tello.move_left(self.distance, 0)
        else:
            self.auto_flight_pause()

    def tello_move_right(self):
        if not self.autoFlightToken:
            self.append_console("Moving Right")
            return self.tello.move_right(self.distance, 0)
        else:
            self.auto_flight_pause()

    def tello_move_up(self):
        if not self.autoFlightToken:
            self.append_console("Moving Upward")
            return self.tello.move_up(self.distance, 0)
        else:
            self.auto_flight_pause()

    def tello_move_down(self):
        if not self.autoFlightToken:
            self.append_console("Moving Downward")
            return self.tello.move_down(self.distance, 0)
        else:
            self.auto_flight_pause()

        # ------------------------- Keyboard press functions ------------------------- #

    def update_track_bar(self):
        self.my_tello_hand.setThr(self.hand_thr_bar.get())

    def setDistanceMeter(self, distance):
        # self.distance = float(distance)/100
        self.distance_bar.amountusedvar.set(int(float(distance)))

    def setDegreeMeter(self, degree):
        # self.degree = newDegree
        self.degree_bar.amountusedvar.set(int(float(degree)))

    def update_distance_bar(self):
        self.distance = round(self.distance_scale.get()/100, 2)
        print('Set distance to %s' % self.distance)
        self.append_console('Set distance to %s' % self.distance)

    def update_degree_bar(self):
        self.degree = round(self.degree_scale.get(), 2)
        print('Set degree angle to %s' % self.degree)
        self.append_console('Set degree angle to %s' % self.degree)

    def on_keypress_w(self, event):
        print("Move up %s m" % self.distance)
        self.tello_move_up()

    def on_keypress_s(self, event):
        print("Move down %s m" % self.distance)
        self.tello_move_down()

    def on_keypress_a(self, event):
        print("Rotate CCW %s degree(s)" % self.degree)
        self.tello_rotate_ccw()

    def on_keypress_d(self, event):
        print("Rotate CW %s degree(s)" % self.degree)
        self.tello_rotate_cw()

    def on_keypress_up(self, event):
        print("Move forward %s m" % self.distance)
        self.tello_move_forward()

    def on_keypress_down(self, event):
        print("Move backward %s m" % self.distance)
        self.tello_move_backward()

    def on_keypress_left(self, event):
        print("Move left %s m" % self.distance)
        self.tello_move_left()

    def on_keypress_right(self, event):
        print("Move right %s m" % self.distance)
        self.tello_move_right()

    def on_keypress_enter(self, event):
        if self.frame is not None:
            self.registerFace()
        self.tmp_f.focus_set()

    # Send command to drone
    def run_preplanned_flight(self, movement, value, delay):
        if movement == "forward":

            description = "Drone is moving forward for " + \
                          str(value) + " cm. Took around " + str(delay) + " seconds"
            self.append_console(description)
            self.tello.move_forward(value, delay)
            # self.tello.send_command(movement + " " + str(value), delay)

        elif movement == "cw":
            description = "Drone is going to turn clockwise " + \
                          str(value) + " degree."
            self.append_console(description)
            self.tello.rotate_cw(value, delay)
            # self.tello.send_command(movement + " " + str(value), delay)

        elif movement == "ccw":
            description = "Drone is going to turn counter-clockwise " + \
                          str(value) + " degree."
            self.append_console(description)
            self.tello.rotate_ccw(value, delay)
            # self.tello.send_command(movement + " " + str(value), delay)

        elif movement == "landing":
            description = "Drone is landing "
            self.append_console(description)
            self.tello.land()
            # self.tello.send_command(movement + " " + str(value), delay)

    # Thread for Automatic Flight
    def flight_thread(self):
        # Pre-planned flight for drone
        checkpoint = self.checkpoint
        i = self.current_checkpoint
        max_round = 5
        self.isStop = False

        self.append_console(
            "==================================================================================")
        if i == 0:
            self.append_console("Switching to Automatic Mode. Starting flight")
            self.append_console("Take off")
            self.tello.takeoff()
        else:
            self.append_console("Continuing automatic flight")

        # Let drone run the pre-planned route 5 times
        while self.current_round <= max_round and self.autoFlightToken:
            print('Round ', self.current_round)
            self.append_console('Round ' + str(self.current_round))

            if self.current_round == max_round:
                self.append_console("Low battery. This is the last round!")

            while i < len(checkpoint) and self.autoFlightToken:
                if (checkpoint[i][0] - 1) < 0:
                    print('At checkpoint ', str(
                        checkpoint[len(checkpoint) - 2][0]))
                    self.append_console(
                        'At checkpoint ' + str(checkpoint[len(checkpoint) - 2][0]))
                else:
                    print(
                        'At checkpoint ', str(checkpoint[i][0] - 1))
                    self.append_console(
                        'At checkpoint ' + str(checkpoint[i][0] - 1))

                self.run_preplanned_flight(
                    checkpoint[i][1], checkpoint[i][2], checkpoint[i][3])
                self.run_preplanned_flight(
                    checkpoint[i][4], checkpoint[i][5], checkpoint[i][6])

                # print('Reached checkpoint ',  str(checkpoint[i][0]))
                # self.append_console('Reached checkpoint '+  str(checkpoint[i][0]))
                self.append_console(
                    "==================================================================================")
                i += 1
                self.current_checkpoint += 1

            if not self.isPause:
                self.current_round += 1

            i = 0

        if self.current_round == max_round and not self.isPause and not self.isStop:
            self.append_console("Returning to charging port")
            print("Returning to charging port")

        if self.isPause:
            self.append_console("Flight paused. Please move to checkpoint " + str(
                self.current_checkpoint) + " to continue Automatic Flight")
            print("Flight paused.")

        elif self.autoFlightToken:
            print("Landing")
            self.append_console("Landing")
            self.tello.land()
            self.append_console("Charging drone")
            print("Charging drone")

        else:
            self.append_console("Flight interrupted. Switching to Manual mode")

        # self.btn_autoFlight.config(relief="raised")
        if self.current_round == max_round:
            self.current_round = 1

    # Start/Stop thread when button is pressed
    def auto_control_flight(self):
        self.btn_autoFlight["state"] = DISABLED
        self.btn_autoFlight_pause["state"] = NORMAL
        self.btn_autoFlight_stop["state"] = NORMAL
        self.autoFlightToken = TRUE
        self.isPause = FALSE
        self.flight_thread()

    # Print to Tkinter console
    def append_console(self, command):
        self.mylist.insert(END, command)
        self.mylist.see("end")
        self.root.update()

    def reset_battery(self):
        self.append_console("Battery reset to 100%")
        print("Battery reset to 100%")

        self.current_round = 1
        self.current_checkpoint = 0

    def auto_flight_pause(self):
        print("Paused")

        self.autoFlightToken = FALSE
        self.isPause = True
        self.btn_autoFlight["state"] = NORMAL
        self.btn_autoFlight_pause["state"] = DISABLED
        self.btn_autoFlight_stop["state"] = NORMAL

    def auto_flight_stop(self):
        print("Stopped")

        self.append_console(
            "==================================================================================")
        self.append_console("Landing")
        self.append_console(
            "Flight has been stopped. Automatic flight will be reset.")

        self.tello.land()
        self.autoFlightToken = FALSE
        self.isStop = True

        self.btn_autoFlight_stop["state"] = DISABLED
        self.btn_autoFlight["state"] = NORMAL
        self.btn_autoFlight_pause["state"] = DISABLED

        self.current_checkpoint = 0

    # Close system
    def on_close(self):
        """
        set the stop event, cleanup the camera, and allow the rest of

        the quit process to continue
        """
        self.loop = False
        print("[INFO] Closing...")
        self.stopEvent.set()

        del self.tello
        self.root.quit()
        self.root.destroy()

        print("[INFO] Program terminated")
