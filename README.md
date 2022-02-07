# WIF3008 Assignment: Rural Medicine Delivery

## Introduction

This is the repository for our team submission for WIF3008 Real Time Systems group assignment for Semester 1, 2021/2022 session. This project requires us to analyse, design, and code a real-time computer program using Python and drone to solve the given problem.

Team Members:
1. **Muhammad Rahiman bin Abdulmanab**
2. **Nur Faidz Hazirah binti Nor'Azman**
3. **Muhammad Luqman bin Sulaiman**
4. **Muhammad Farouq bin Shaharuddin**
   
   
## Problem Statements

In the healthcare context, the timely delivery of medications, vaccines and blood is crucial. Urgent medical services can easily be interrupted due to traffic jams especially in large urban areas. Supply challenges are also frequently caused by poor transport networks, extreme weather conditions, natural disasters, or traffic congestion in urban areas. Any delays in delivery could potentially lead to loss of life. 

Furthermore, delivering critical medical supplies in hard-to-reach rural areas can be problematic when using normal modes of transports due to multiple factors such as difficult terrain and weather. A lack of access to all-weather roads is one of the biggest challenges facing affordable healthcare provision in rural areas especially in the developing world. Since many roads in these rural areas are inaccessible during rainy seasons, their population are hindered from life-saving and critical health products. Where modes of delivery like truck, motorcycle and boat are not viable, clinics can be left without essential medical supplies.

In addition, blood and plasma have short shelf lives and must be transported in very specific conditions. As do vaccines, as some require refrigeration. This challenging terrain and gaps in infrastructure contribute to why at least half the world’s population lacks access to essential health products and services. This healthcare access disparity can be especially damaging to these remote communities.

## Software Design


## Requirements

### Functional Requirements

The following are the functional requirements of the system:

|   ID  |                                                                                               Requirements                                                                                               |                Use Case               |
|:-----:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:-------------------------------------:|
| F-001 | The system shall be able to control the drone via the Control Panel GUI.                                                                                                                                 |          Deploy drone (UC-1)          |
| F-002 | The system shall be able to program the drone to follow a pre-planned route.                                                                                                                             |          Deploy drone  (UC-1)         |
| F-003 | The system shall be able to pause the drone’s automatic flight in its pre-planned route using the Control Panel GUI.                                                                                     | Pause drone’s automatic flight (UC-4) |
| F-004 | The system shall be able to stop the drone’s automatic flight in its pre-planned route at any given time using the Control Panel GUI.                                                                    |  Stop drone’s automatic flight (UC-5) |
| F-005 | The system shall allow the user to override the drone’s pre-planned route execution to manual control at any given time using the Control Panel GUI.                                                     |          Control drone (UC-3)         |
| F-006 | The system shall be able to control the drone’s orientation (yaw), forward/backward movement (pitch), altitude (throttle) and left/right movement (roll) from the Control Panel GUI using keyboard keys. |          Control drone (UC-3)         |
| F-007 | The system shall allow the user to flip the drone in multiple directions (backward, forward, right, left) using the Control Panel GUI.                                                                   |           Flip drone (UC-6)           |
| F-008 | The system shall allow the user to adjust the flight distance of the drone in meters using the Control Panel GUI.                                                                                        | Adjust drone’s flight distance (UC-7) |
| F-009 | The system shall allow the user to adjust the flight rotation angle of the drone in degrees using the Control Panel GUI.                                                                                 | Adjust drone’s flight rotation (UC-8) |
| F-010 | The system shall allow the user to reset the distance and rotation angle from the Control Panel GUI.                                                                                                     | Adjust drone’s flight distance (UC-7) |
|       |                                                                                                                                                                                                          | Adjust drone’s flight rotation (UC-8) |
| F-011 | The system shall allow the user to take-off and land the drone at any given time using the Control Panel GUI.                                                                                            |     Take off and land drone (UC-2)    |
| F-012 | The system shall be able to detect gestures using image processing.                                                                                                                                      |          Detect gesture(UC-9)         |
| F-013 | The system shall allow the user to control the drone using hand gesture.                                                                                                                                 |                                       |
| F-014 | The system shall be able to display the drone’s current flight details (path, mode and movement) in the Control Panel GUI.                                                                               |  View current flight details (UC-10)  |

### Quality Requirements

The following are the quality requirements of the system based on the eight ISO/IEC 25010 software product quality model (https://iso25000.com/index.php/en/iso-25000-standards/iso-25010):

<img width="451" alt="image" src="https://user-images.githubusercontent.com/50654608/152883542-b2698725-ab79-4ab8-8862-ca83788f4c61.png">

|   ID  |                                                                                               Requirements                                                                                               |           Quality Attribute           |    Quality Criteria    |
|:-----:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:-------------------------------------:|:----------------------:|
| Q-001 | The system should be able to send commands to the drone within 1 second.                                                                                                                                 |         Performance Efficiency        |     Time Behaviour     |
| Q-002 | The system should be able to adapt to the drone quickly and do the tasks handled by the user.                                                                                                            |              Portability              |      Adaptability      |
| Q-003 | The system should be able to regain control after losing control and land in a "safe" area in the event of mechanical or battery failure.                                                                |              Reliability              |     Recoverability     |
| Q-004 | The system should be able to execute the tasks moving the drone with precise distance, height and degree flight.                                                                                         |         Functional Suitability        | Functional Correctness |
| F-005 | The system shall allow the user to override the drone’s pre-planned route execution to manual control at any given time using the Control Panel GUI.                                                     |          Control drone (UC-3)         |                        |
| F-006 | The system shall be able to control the drone’s orientation (yaw), forward/backward movement (pitch), altitude (throttle) and left/right movement (roll) from the Control Panel GUI using keyboard keys. |          Control drone (UC-3)         |                        |
| F-007 | The system shall allow the user to flip the drone in multiple directions (backward, forward, right, left) using the Control Panel GUI.                                                                   |           Flip drone (UC-6)           |                        |
| F-008 | The system shall allow the user to adjust the flight distance of the drone in meters using the Control Panel GUI.                                                                                        | Adjust drone’s flight distance (UC-7) |                        |
| F-009 | The system shall allow the user to adjust the flight rotation angle of the drone in degrees using the Control Panel GUI.                                                                                 | Adjust drone’s flight rotation (UC-8) |                        |
| F-010 | The system shall allow the user to reset the distance and rotation angle from the Control Panel GUI.                                                                                                     | Adjust drone’s flight distance (UC-7) |                        |
|       |                                                                                                                                                                                                          | Adjust drone’s flight rotation (UC-8) |                        |
| F-011 | The system shall allow the user to take-off and land the drone at any given time using the Control Panel GUI.                                                                                            |     Take off and land drone (UC-2)    |                        |
| F-012 | The system shall be able to detect gestures using image processing.                                                                                                                                      |          Detect gesture(UC-9)         |                        |
| F-013 | The system shall allow the user to control the drone using hand gesture.                                                                                                                                 |                                       |                        |
| F-014 | The system shall be able to display the drone’s current flight details (path, mode and movement) in the Control Panel GUI.                                                                               |  View current flight details (UC-10)  |                        |

### Constraints

The following are the constraints or limitations of the system together with their descriptions:

|   ID  |                                                                                               Requirements                                                                                               |   |
|:-----:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|---|
| C-001 | The flight altitude is limited to 32.8 ft. (10 m).                                                                                                                                                       |   |
| C-002 | The flight distance is limited to 328 ft. (100 m).                                                                                                                                                       |   |
| C-003 | The drone cannot be used in adverse weather conditions such as rain, snow, fog, wind, smog, hail, lightning, tornadoes, or hurricanes.                                                                   |   |
| C-004 | The drone can only fly at least 33 ft. (10 m) away from obstacles, people, animals, buildings, public infrastructure, trees, and bodies of water when in flight.                                         |   |
| C-005 | The drone cannot fly on a route that has an abrupt change in the ground level (such as from inside a building to outside), otherwise the positioning function may be disrupted and affect flight safety. |   |
| C-006 | The drone and battery performance are subject to environmental conditions such as air density and temperature.                                                                                           |   |
| C-007 | The drone is not recommended to fly in the presence of wireless equipment to avoid interference between your smart device and other wireless equipment.                                                  |   |
| C-008 | The drone cannot fly in areas where the magnetic or radio interference may occur to avoid disrupting the communication between the aircraft and the remote-control device.                               |   |

## Software Design

### Use Case Diagram

<img width="451" alt="image" src="https://user-images.githubusercontent.com/50654608/152883691-cbc6ab98-8ceb-44c9-b1a7-f3402e1b296a.png">

### Activity Diagram

<img width="495" alt="image" src="https://user-images.githubusercontent.com/50654608/152883724-07c451db-d01c-4adf-a15c-f464f49e6130.png">
<img width="479" alt="image" src="https://user-images.githubusercontent.com/50654608/152883737-5cd33172-7d7d-4b51-8d2c-d83b217b6250.png">

## Implementation

### Control Panel GUI

<img width="451" alt="image" src="https://user-images.githubusercontent.com/50654608/152883766-ff60465a-ef16-468e-aafd-8134f6a35497.png">

A GUI is implemented to provide an easy access control to the drone. The control panel consists of buttons to manage the drone’s functionalities and also display the route information. A common package, Tkinter, is being used to implement the GUI design along with ttkbootstrap, which is a built-in package and theme extension for Tkinter that enables on-demand modern flat style themes inspired by Bootstrap.
