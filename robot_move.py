import stretch_body.robot as rb
from stretch_body.robot_params import RobotParams
from functools import partial


class RobotMove:
    def __init__(self, robot, speed='default'):
        
        self.params = RobotParams().get_params()[1]
        self.available_speeds = ['default', 'slow', 'fast', 'max']
        self.create_all_commands(robot)

        if speed not in self.all_speeds.keys():
            print('WARNING: RobotMove create_commands called with unrecognized speed = \'' + speed + '\'')
            print('         Using \'default\' speed instead.')
            speed = 'default'
        
        self.speed = speed
        self.move_to_functions = self.all_speeds[self.speed]['move_to_functions']
        self.move_to_settings = self.all_speeds[self.speed]['move_to_settings']
        

    def print_settings(self):
        print(self.move_to_settings)

    def create_all_commands(self, robot):
        self.all_speeds = {}
        for speed in self.available_speeds:

            base_speed = self.params['base']['motion'][speed]
            base_rot_v = base_speed['vel_m']
            base_rot_a = base_speed['accel_m']

            lift_speed = self.params['lift']['motion'][speed]
            lift_v = lift_speed['vel_m']
            lift_a = lift_speed['accel_m']

            arm_speed = self.params['arm']['motion'][speed]
            arm_v = arm_speed['vel_m']
            arm_a = arm_speed['accel_m']

            yaw_speed = self.params['wrist_yaw']['motion'][speed]
            yaw_v = yaw_speed['vel']
            yaw_a = yaw_speed['accel']

            pitch_speed = self.params['wrist_pitch']['motion'][speed]
            pitch_v = pitch_speed['vel']
            pitch_a = pitch_speed['accel']

            roll_speed = self.params['wrist_roll']['motion'][speed]
            roll_v = roll_speed['vel']
            roll_a = roll_speed['accel']

            gripper_speed = self.params['stretch_gripper']['motion'][speed]
            gripper_v = gripper_speed['vel']
            gripper_a = gripper_speed['accel']

            # # stretch gripper move_to
            # def move_to(self,pct, v_r=None, a_r=None):
            #     """
            #     pct: commanded absolute position (Pct).
            #     v_r: velocity for trapezoidal motion profile (rad/s).
            #     a_r: acceleration for trapezoidal motion profile (rad/s^2)
            #     """

            move_to_functions = {
                'joint_mobile_base_rotate_by': partial(robot.base.rotate_by, v_r=base_rot_v, a_r=base_rot_a),
                'joint_lift': partial(robot.lift.move_to, v_m=lift_v, a_m=lift_a), 
                'joint_arm_l0': partial(robot.arm.move_to, v_m=lift_v, a_m=lift_a), 
                'joint_wrist_yaw': partial(robot.end_of_arm.move_to, 'wrist_yaw', v_r=yaw_v, a_r=yaw_a),
                'joint_wrist_pitch': partial(robot.end_of_arm.move_to, 'wrist_pitch', v_r=pitch_v, a_r=pitch_a),
                'joint_wrist_roll': partial(robot.end_of_arm.move_to, 'wrist_roll', v_r=roll_v, a_r=roll_a),
                'stretch_gripper' : partial(robot.end_of_arm.move_to, 'stretch_gripper', v_r=gripper_v, a_r=gripper_a)
            }

            move_to_settings = {
                'joint_mobile_base_rotate_by': (None, {'v_r':base_rot_v, 'a_r':base_rot_a}),
                'joint_lift': (None, {'v_m':lift_v, 'a_m':lift_a}), 
                'joint_arm_l0': (None, {'v_m':lift_v, 'a_m':lift_a}), 
                'joint_wrist_yaw': ('wrist_yaw', {'joint': 'wrist_yaw','v_r':yaw_v, 'a_r':yaw_a}),
                'joint_wrist_pitch': ('wrist_pitch', {'joint': 'wrist_pitch','v_r':pitch_v, 'a_r':pitch_a}),
                'joint_wrist_roll': ('wrist_roll', {'joint': 'wrist_roll', 'v_r':roll_v, 'a_r':roll_a}),
                'stretch_gripper' : ('stretch_gripper', {'joint': 'stretch_gripper', 'v_r':gripper_v, 'a_r':gripper_a})
            }

                
            self.all_speeds[speed] = {'move_to_functions': move_to_functions, 'move_to_settings': move_to_settings}
                
        

    def clip_configuration(self, config, min_config, max_config):
        pass
        
    def to_configuration(self, config, valid_joints=None, speed=None):
        if speed is None:
            move_to_functions = self.move_to_functions
        else:
            if speed not in self.all_speeds.keys():
                print('WARNING: RobotMove create_commands called with unrecognized speed = \'' + speed + '\'')
                print('         Using \'default\' speed instead.')
                speed = 'default'
            move_to_functions = self.all_speeds[ ]['move_to_functions']
            
        for j in config.keys():
            if valid_joints is None:
                move_to_functions[j](config[j])
            elif j in valid_joints: 
                move_to_functions[j](config[j])
            

                
if __name__ == '__main__':
    
    robot = rb.Robot()
    robot.startup()
    
    robot_move = RobotMove(robot, speed='slow')
    robot_move.print_settings()

    starting_configuration = {
        'base_link_shoulder_pan_joint': 0.0,
        'shoulder_pan_shoulder_lift_joint': 0.0,
        'shoulder_lift_elbow_joint': 0.0,
        'elbow_wrist_1_joint': 0.0,
        'wrist_1_wrist_2_joint': 0.0
    }
    
    robot_move.to_configuration(starting_configuration, speed='slow')
    robot.push_command()
    robot.wait_command()
    robot.stop()
    
