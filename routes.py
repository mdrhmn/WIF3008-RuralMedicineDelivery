class Route:
    # Checkpoint, Movement, Value (dist/angle), Delay
    # checkpoint = [[1, "ccw", 90, 1, "forward", 100, 5], [2, "ccw", 90, 1, "forward", 80, 4],
    #               [3, "ccw", 90, 1, "forward", 40, 2], [
    #               4, "cw", 90, 1, "forward", 60, 3],
    #               [5, "ccw", 90, 1, "forward", 40, 2], [0, "ccw", 90, 1, "forward", 40, 2]]

    checkpoint = [  
        # 0 -> 1
                    [0, "cw", 90, 1, "forward", 250, 2],
                    # 1 -> 2
                    [1, "cw", 90, 1, "forward", 150, 5],

                    # 2 -> 3,
                    [2, "cw", 90, 1, "forward", 250, 4],

                    # 3 -> 4,
                    [3, "ccw", 90, 1, "forward", 150, 2], 

                    # 4 -> 5
                    [4, "cw", 90, 1, "forward", 250, 3],
                    
                    # 5 -> 6
                    [5, "ccw", 90, 1, "forward", 100, 2],
                    
                    # 6 -> 7
                    [6, "ccw", 90, 1, "forward", 150, 2]
                ]

# 1. take off [0]
# 2. rotate clockwise 90* [0]
# 3. move forward [0-->1]
# 4. rotate clockwise 90* [1]
# 5. move forward [1->2]
# 6. rotate clockwise 90* [2]
# 7. move forward [2->3]
# 8. rotate  counter clockwise 90* [3]
# 9. move forward [3->4]
# 10. rotate  counter clockwise 90* [4]
# 11. move forward [4->5]
# 12. rotate clockwise 90* [5]
# 13. move forward [5->6]
# 14. rotate clockwise 90* [6]
# 15. move forward [6->7]