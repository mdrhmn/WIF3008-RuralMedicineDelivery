from tello_control_ui import TelloUI
import routes
import tello


def main():
    # Running the system:
	
    # 1) Without simulator
    # open main.py and user port = 8889
    # run main.py

    # 2) With simulator (you can see the simulator receiving the instruction)
    # run TelloSimulator.py in cmd using python TelloSimulator.py
    # run main.py with port = 9000

    # port = 9000
    port = 8889

    drone = tello.Tello('', port)
    route = routes.Route.checkpoint
    vplayer = TelloUI(drone, route, "./img/")

    # Start the Tkinter mainloop
    vplayer.root.mainloop()


if __name__ == "__main__":
    main()
