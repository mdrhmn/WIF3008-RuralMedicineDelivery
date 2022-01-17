from gestures.gesture_recognition import GestureRecognition, GestureBuffer
from utils import CvFpsCalc
import ttkbootstrap as ttk
import ttkbootstrap
import tkinter as tki
from tkinter import *
import configargparse
import threading
import datetime
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
        print(self.checkpoint)

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
        self.distance = 20  # default distance for 'move' cmd
        self.degree = 0  # default degree for 'cw' or 'ccw' cmd
        self.current_gesture_id = None
        self.isLand = True
        self.onGesture = False

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

        # -------------------------------- Gesture Frame ------------------------------- #

        # Create buttons
        red_zone_2 = Frame(self.root)
        red_zone_2.pack(fill="both", expand="yes",
                        side="bottom", pady=20, padx=20)

        video_frame = LabelFrame(red_zone_2, text="Gesture Control")
        video_frame.pack(fill="both", expand="yes", side="left")

        self.btn_startGesture = ttk.Button(video_frame, text="Start Gesture", bootstyle='primary',
                                           command=self.start_gesture)
        self.btn_startGesture.pack(side="top", fill="both",
                                   expand="yes", padx=10, pady=5)

        self.btn_stopGesture = ttk.Button(
            video_frame, bootstyle='warning', text="Stop Gesture", command=self.stop_gesture)
        self.btn_stopGesture.pack(side="top", fill="both",
                                  expand="yes", padx=10, pady=5)

        # -------------------------- Automatic Flight Frame -------------------------- #

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
                                      amountused=self.distance,
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
        self.distance_scale.set(self.distance)

        # --------------------------------- Column 2 --------------------------------- #

        col2 = LabelFrame(blue_zone, text="Second Panel")
        col2.pack(fill="both", expand="yes", side="left")

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
                                    interactive=False)
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

        self.btn_moveleft = ttk.Button(
            first_btn_set, text="Move Left", bootstyle='secondary', command=self.tello_move_left)
        self.btn_moveleft.pack(side="left")

        self.btn_moveright = ttk.Button(
            first_btn_set, text="Move Right", bootstyle='secondary', command=self.tello_move_right)
        self.btn_moveright.pack(side="right")

        self.btn_moveforward = ttk.Button(
            first_btn_set, text="Move Forward", bootstyle='secondary', command=self.tello_move_forward)
        self.btn_moveforward.pack(side="top", pady=10)

        self.btn_movebackward = ttk.Button(
            first_btn_set, text="Move Backward", bootstyle='secondary', command=self.tello_move_backward)
        self.btn_movebackward.pack(side="bottom", pady=10)

        # -------------------------- Rotation, Up/Down Frame ------------------------- #

        second_btn_set = Frame(green_zone_1)
        second_btn_set.pack(fill="both", expand="yes",
                            side="left", padx=50)

        self.btn_rotatecw = ttk.Button(
            second_btn_set, text="Rotate CW", bootstyle='secondary', command=self.tello_rotate_cw)
        self.btn_rotatecw.pack(side="left")

        self.btn_rotateccw = ttk.Button(
            second_btn_set, text="Rotate CCW", bootstyle='secondary', command=self.tello_rotate_ccw)
        self.btn_rotateccw.pack(side="right")

        self.btn_moveup = ttk.Button(
            second_btn_set, text="Move Up", bootstyle='secondary', command=self.tello_move_up)
        self.btn_moveup.pack(side="top", pady=10)

        self.btn_movedown = ttk.Button(
            second_btn_set, text="Move Down", bootstyle='secondary', command=self.tello_move_down)
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
        # self.thread = threading.Thread(target=self.webcam_feed, args=())
        # self.thread.setDaemon(True)
        # self.thread.start()

        # Set a callback to handle when the window is closed
        self.root.wm_title("Tello Drone Controller")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.on_close)
        self.loop = True

        while self.loop:
            self.root.update()

    # def webcam_feed(self):

    #     print('## Reading configuration ##')
    #     parser = configargparse.ArgParser(default_config_files=['config.txt'])

    #     parser.add('-c', '--my-config', required=False, is_config_file=True, help='config file path')
    #     parser.add("--device", type=int)
    #     parser.add("--width", help='cap width', type=int)
    #     parser.add("--height", help='cap height', type=int)
    #     parser.add("--is_keyboard", help='To use Keyboard control by default', type=bool)
    #     parser.add('--use_static_image_mode', action='store_true', help='True if running on photos')
    #     parser.add("--min_detection_confidence",
    #                help='min_detection_confidence',
    #                type=float)
    #     parser.add("--min_tracking_confidence",
    #                help='min_tracking_confidence',
    #                type=float)
    #     parser.add("--buffer_len",
    #                help='Length of gesture buffer',
    #                type=int)

    #     args = parser.parse_args()

    #     gesture_detector = GestureRecognition(args.use_static_image_mode, args.min_detection_confidence,
    #                                           args.min_tracking_confidence)
    #     gesture_buffer = GestureBuffer(buffer_len=args.buffer_len)
    #     cv_fps_calc = CvFpsCalc(buffer_len=10)

    #     mode = 0
    #     number = -1

    #     cap = cv2.VideoCapture(0)

    #     while (True):
    #         # Capture the video frame by frame
    #         ret, frame = cap.read()
    #         fps = cv_fps_calc.get()
    #         image = frame

    #         debug_image, gesture_id = gesture_detector.recognize(image, number, mode)
    #         gesture_buffer.add_gesture(gesture_id)

    #         self.gesture_control(gesture_buffer)

    #         debug_image = gesture_detector.draw_info(debug_image, fps, mode, number)
    #         cv2.imshow('Tello Gesture Recognition', debug_image)

    #         key = cv2.waitKey(1) & 0xff
    #         if key == 27:  # ESC
    #             break

    #     # After the loop release the cap object
    #     cap.release()

    #     # Destroy all the windows
    #     cv2.destroyAllWindows()

    def gesture_control(self, gesture_buffer):
        gesture_id = gesture_buffer.get_gesture()

        if not self.isLand and gesture_id != None and self.onGesture == True:

            if gesture_id == 0:  # FORWARD
                self.tello.move_forward(50, 0)

                if self.current_gesture_id != gesture_id:
                    print("[GESTURE] Moving Forward")

            elif gesture_id == 1:  # STOP
                self.tello.move_forward(0, 0)
                self.tello.move_backward(0, 0)
                self.tello.move_up(0, 0)
                self.tello.move_down(0, 0)
                self.tello.move_left(0, 0)
                self.tello.move_right(0, 0)

                if self.current_gesture_id != gesture_id:
                    print("[GESTURE] Stop")

            if gesture_id == 5:  # BACKWARD
                self.tello.move_backward(50, 0)

                if self.current_gesture_id != gesture_id:
                    print("[GESTURE] Moving Backward")

            elif gesture_id == 2:  # UP
                self.tello.move_up(50, 0)

                if self.current_gesture_id != gesture_id:
                    print("[GESTURE] Moving Upward")

            elif gesture_id == 4:  # DOWN
                self.tello.move_down(50, 0)

                if self.current_gesture_id != gesture_id:
                    print("[GESTURE] Moving Downward")

            elif gesture_id == 3:  # LAND
                self.tello.land()
                self.isLand = True

                if self.current_gesture_id != gesture_id:
                    print("[GESTURE] Landing")

            elif gesture_id == 6:  # LEFT
                self.tello.move_left(50, 0)

                if self.current_gesture_id != gesture_id:
                    print("[GESTURE] Moving Left")

            elif gesture_id == 7:  # RIGHT
                self.tello.move_right(50, 0)

                if self.current_gesture_id != gesture_id:
                    print("[GESTURE] Moving Right")

            elif gesture_id == -1:  # NO ACTION
                self.tello.move_forward(0, 0)
                self.tello.move_backward(0, 0)
                self.tello.move_up(0, 0)
                self.tello.move_down(0, 0)
                self.tello.move_left(0, 0)
                self.tello.move_right(0, 0)

                if self.current_gesture_id != gesture_id:
                    print("[GESTURE] No Action")

            self.current_gesture_id = gesture_id

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

    def start_gesture(self):
        self.onGesture = True
        self.append_console("Gesture on")
        print("Drone starts following gesture instructions")

    def stop_gesture(self):
        self.onGesture = False
        self.append_console("Gesture off")
        print("Drone stops following gesture instructions")

    # ---------------------------------------------------------------------------- #
    #                          TELLO DRONE FUNCTIONALITIES                         #
    # ---------------------------------------------------------------------------- #

    def tello_take_off(self):
        if not self.autoFlightToken:
            self.append_console("Take off")
            self.isLand = False
            return self.tello.takeoff()
        else:
            self.auto_flight_pause()

    def tello_landing(self):
        if not self.autoFlightToken:
            self.append_console("Landing")
            self.isLand = True
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
        self.distance = int(self.distance_scale.get())
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
        print(checkpoint, ' checkpoint')
        print(self.current_checkpoint, ' self.current_checkpoint')
        i = self.current_checkpoint
        print(i, ' i')
        max_round = 5
        self.isStop = False

        self.append_console(
            "==================================================================================")
        if i == 0:
            self.append_console("Switching to Automatic Mode. Starting flight")
            self.append_console("Take off")
            self.tello.takeoff()
            self.isLand = False
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
        self.isLand = True
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

