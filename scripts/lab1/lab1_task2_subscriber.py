#!/usr/bin/env python
# license removed for brevity

import rospy
from geometry_msgs.msg import *
from nav_msgs.msg import *
from std_msgs.msg import String
import math
import threading
from tf.transformations import euler_from_quaternion, quaternion_from_euler

velocity_x=0.5
velocity_y=0.5
velocity_theta=0.5

angle_moved=0
current_orientation=0
previous_orientation=0

distance=0
distance_moved=0
previous_position=Point(0,0,0)
current_position=Point(0,0,0)

vel_msg=Twist()

velocity_publisher = rospy.Publisher('/mux_vel_nav/cmd_vel', Twist, queue_size=10)
move_pose = geometry_msgs.msg.Pose()

turn_odom=1

poses=PoseStamped()

def callback11(data):
    x=1

global odom_subscriber
odom_subscriber=rospy.Subscriber('/elektron/mobile_base_controller/odom',Odometry, callback11)


def callback(data):
    print("\n")
    rospy.loginfo("I have new message")
    talker(data) 
    
    
def move_beginner(pose):
    global move_pose
    global vel_msg
    global odom_subscriber
    global turn_odom
    global angle_moved
    global previous_orientation
    global current_orientation
    global distance
    global distance_moved
    global previous_position
    global current_position
    
    angle_moved=0
    distance_moved=0
    
    turn_odom=rospy.wait_for_message('/elektron/mobile_base_controller/odom',Odometry)
    
    orientation_q = turn_odom.pose.pose.orientation

    orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
    (roll, pitch, yaw) = euler_from_quaternion (orientation_list)
    current_orientation=abs(yaw)
    previous_orientation=abs(yaw)
    
    current_position=turn_odom.pose.pose.position
    previous_position=turn_odom.pose.pose.position
   # print(turn_odom)
    odom_subscriber=rospy.Subscriber('/elektron/mobile_base_controller/odom',Odometry, turn)


    vel_msg = Twist()
    stop_msg = Twist()
    
    distance=math.sqrt(pow(pose.position.x,2)+pow(pose.position.y,2))
    cos_x=1
    
    if(distance>0):
        cos_x=pose.position.x/distance
    
    theta_start=math.acos(cos_x)
    
    move_pose.position.x = pose.position.x
    move_pose.position.y = pose.position.y
    

    if(pose.position.y>=0):
        vel_msg.angular.z=velocity_theta
        move_pose.orientation.z = turn_odom.pose.pose.orientation.z-theta_start
    else:
        vel_msg.angular.z=-velocity_theta
        move_pose.orientation.z = turn_odom.pose.pose.orientation.z+theta_start
    
    move_pose.orientation.z=theta_start
    velocity_publisher.publish(vel_msg)    
    

def forward(data):
    global distance
    global distance_moved
    global previous_position
    global current_position
    global poses

    
    
    current_position=data.pose.pose.position
    diff_x=current_position.x-previous_position.x
    diff_y=current_position.y-previous_position.y
    distance_moved +=math.sqrt(pow(diff_x,2)+pow(diff_y,2))
    previous_position=current_position
    
    print("\nforward data")
    print("distance: %f" % distance)
    print("distance moved: %f" % distance_moved)
   
    
    if(distance_moved>distance):
        print("end of forward movement")
        #vel_msg=Twist([ve])
        stop_msg = Twist()
        velocity_publisher.publish(stop_msg)
        
        odom_subscriber.unregister()
        try:
            move_beginner(poses.pop(0).pose)
        except:
            pass

def turn(data):
    global move_pose

    global velocity_publisher
    global  vel_msg
    global odom_subscriber
    global angle_moved
    global previous_orientation
    global current_orientation

    orientation_q = data.pose.pose.orientation
    orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
    (roll, pitch, yaw) = euler_from_quaternion (orientation_list)
    current_orientation=abs(yaw)
    angle_moved+= abs(current_orientation-previous_orientation)
    previous_orientation=current_orientation
    

    print("turn data")
    print(move_pose.orientation.z)
    print(data.pose.pose.orientation.z)
    print("yaw: %f" %yaw)
    print("angle moved: %f"%angle_moved)
    
  
    if(angle_moved>=move_pose.orientation.z):
        print("end of turn movement")
        #vel_msg=Twist()
        velocity_publisher.publish(Twist())
        rospy.sleep(0.1)
        
        stop_msg = Twist(Vector3(velocity_x, 0, 0),Vector3(0,0,0))
       
        velocity_publisher.publish(stop_msg)
        
        odom_subscriber.unregister()
        odom_subscriber=rospy.Subscriber('/elektron/mobile_base_controller/odom',Odometry, forward)


def talker(data):
    global poses
    poses=data.poses
    move_beginner(poses.pop(0).pose)
   
    



def main():
    rospy.init_node('listener23', anonymous=True)
    odom_subscriber.unregister()
    print("start")
    rospy.Subscriber("chatter", Path, callback)
    #rospy.Subscriber("chatter", Pose, callback)

  
    rospy.spin()

if __name__=='__main__':
	main()
