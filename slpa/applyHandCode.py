# Import statements
import re
from collections import OrderedDict
from copy import deepcopy
import mathutils
import math
import numpy as numpy
from numpy.linalg import norm
from numpy import dot
from math import pi ,sin, cos
import os
import sys
import bpy

"""
To Run in Blender:
    filename = 'C:\\Users\\Scott\\Documents\\GitHub\\SLP-Annotator\\slpa\\applyHandCode.py'
    exec(compile(open(filename).read(), filename, 'exec'))

To Reset Blender Model:
    bpy.ops.ed.undo_history(item=0)
"""

def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = numpy.asarray(axis)
    axis = axis/math.sqrt(numpy.dot(axis, axis))
    a = math.cos(theta/2.0)
    b, c, d = -axis*math.sin(theta/2.0)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return numpy.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])

def rotation_from_matrix(matrix):
    """Return rotation angle and axis from rotation matrix.

    >>> angle = (random.random() - 0.5) * (2*math.pi)
    >>> direc = numpy.random.random(3) - 0.5
    >>> point = numpy.random.random(3) - 0.5
    >>> R0 = rotation_matrix(angle, direc, point)
    >>> angle, direc, point = rotation_from_matrix(R0)
    >>> R1 = rotation_matrix(angle, direc, point)
    >>> is_same_transform(R0, R1)
    True

    """
    R = numpy.array(matrix, dtype=numpy.float64, copy=False)
    R33 = R[:3, :3]
    # direction: unit eigenvector of R33 corresponding to eigenvalue of 1
    w, W = numpy.linalg.eig(R33.T)
    i = numpy.where(abs(numpy.real(w) - 1.0) < 1e-8)[0]
    if not len(i):
        raise ValueError("no unit eigenvector corresponding to eigenvalue 1")
    direction = numpy.real(W[:, i[-1]]).squeeze()
    # point: unit eigenvector of R33 corresponding to eigenvalue of 1
    w, Q = numpy.linalg.eig(R)
    i = numpy.where(abs(numpy.real(w) - 1.0) < 1e-8)[0]
    if not len(i):
        raise ValueError("no unit eigenvector corresponding to eigenvalue 1")
    point = numpy.real(Q[:, i[-1]]).squeeze()
    point /= point[3]
    # rotation angle depending on direction
    cosa = (numpy.trace(R33) - 1.0) / 2.0
    if abs(direction[2]) > 1e-8:
        sina = (R[1, 0] + (cosa-1.0)*direction[0]*direction[1]) / direction[2]
    elif abs(direction[1]) > 1e-8:
        sina = (R[0, 2] + (cosa-1.0)*direction[0]*direction[2]) / direction[1]
    else:
        sina = (R[2, 1] + (cosa-1.0)*direction[1]*direction[2]) / direction[0]
    angle = math.atan2(sina, cosa)
    return angle, direction, point

# Function to translate handshape coding to degrees of rotation, adduction, flexion
def translate_finger_code_to_degrees(finger, hand, Fshape, handShapeParams):
    # flexionDictionary parameters: [proximal, medial, distal] joints
    if hand == 'L':
        flexionDict = {'H':[25, 15, 10], 'E':[7, 5, 5], 'e': [5, 0, 0], 'i':[-30, -35, -40], 'f':[-30, -35, -40], 'F':[-80, -90, -75], '_':[0, 0, 0]}
        abductDict = {'middle': {'x': -30, '=':0, '<':10, '{':15, '_':0}, 'ring': {'x': -25, '=':0, '<':10, '{':15, '_':0}, 'pinky': {'x': -25, '=':0, '<':10, '{':15, '_':0}}
        rotDict = {'middle': {'x': -10, '=':0, '<':5, '{':7, '_':0}, 'ring': {'x': -10, '=':0, '<':-5, '{':-7, '_':0}, 'pinky': {'x': -10, '=':0, '<':-10, '{':-12, '_':0}}
    else:
        flexionDict = {'H':[-25, -15, -10], 'E':[-7, -5, -5], 'e': [-5, 0, 0], 'i':[30, 35, 40], 'f':[30, 35, 40], 'F':[80, 90, 75], '_':[0, 0, 0]}
        abductDict = {'middle': {'x': 30, '=':0, '<':-10, '{':-15, '_':0}, 'ring': {'x': 25,'=':0, '<':-10, '{':-15, '_':0}, 'pinky': {'x':25, '=':0, '<':-10, '{':-15, '_':0}}
        rotDict = {'middle': {'x': 10, '=':0, '<':5, '{':7, '_':0}, 'ring': {'x': 10, '=':0, '<':-5, '{':-7, '_':0}, 'pinky': {'x': 10, '=':0, '<':-10, '{':-12, '_':0}}

    if finger == 'index':
        handShapeParams['finger_index.01.' + hand] = [0, 0, flexionDict[Fshape[1]][0]]
        handShapeParams['finger_index.02.' + hand] = [0, 0, flexionDict[Fshape[2]][1]]
        handShapeParams['finger_index.03.' + hand] = [0, 0, flexionDict[Fshape[3]][2]]
    else:
        # Parameters: [adduction, rotation, flexion]
        handShapeParams['finger_' + finger + '.01.' + hand] = [abductDict[finger][Fshape[0]], rotDict[finger][Fshape[0]], flexionDict[Fshape[2]][0]]
        handShapeParams['finger_' + finger + '.02.' + hand] = [0, rotDict[finger][Fshape[0]], flexionDict[Fshape[3]][1]]
        handShapeParams['finger_' + finger + '.03.' + hand] = [0, rotDict[finger][Fshape[0]], flexionDict[Fshape[4]][2]]
    return handShapeParams

def translate_thumb_code_to_degrees(hand, Tshape, handShapeParams):
    if hand == 'L':
        if Tshape[0] == 'O':
            flexionDict = {'H':[-20, -10], 'E':[-10, -5], 'e': [15, 15], 'i':[30, 25], 'F':[80, 25], '_':[0, 0]}
        elif Tshape[0] == 'L':
            flexionDict = {'H':[-20, -10], 'E':[-10, -5], 'e': [15, 15], 'i':[30, 25], 'F':[85, 35], '_':[0, 0]}
        else:
            flexionDict = {'H':[0, 0], 'E':[50, 0], 'e': [0, 0], 'i':[60, 0], 'F':[80, 0], '_':[0, 0]}
    elif hand == 'R':
        if Tshape[0] == 'O':
            flexionDict = {'H':[20, -10], 'E':[10, -5], 'e': [-15, 15], 'i':[-30, 25], 'F':[-80, 25], '_':[0, 0]}
        elif Tshape[0] == 'L':
            flexionDict = {'H':[20, -10], 'E':[10, -5], 'e': [-15, 15], 'i':[-30, 25], 'F':[-85, 35], '_':[0, 0]}
        else:
            flexionDict = {'H':[0, 0], 'E':[50, 0], 'e': [0, 0], 'i':[60, 0], 'F':[80, 0], '_':[0, 0]}

    # Sample Code: Tshape:[L=EH]
    #handShapeParams['thumb.02.' + hand] = [0, 0, 0]
    #handShapeParams['thumb.03.' + hand] = [0, 0, 0]    
    if hand == 'L':
        if Tshape[0] == 'U' and Tshape[1] == '=':
            handShapeParams['thumb.01.' + hand + '.001'] = [-10, -25, 0]
        elif Tshape[0] == 'U' and Tshape[1] == '<':
            handShapeParams['thumb.01.' + hand + '.001'] = [10, -25, 0]

        elif Tshape[0] == 'O' and Tshape[1] == '=':
            handShapeParams['thumb.01.' + hand + '.001'] = [15, -20, 5]
        elif Tshape[0] == 'O' and Tshape[1] == '<':
            handShapeParams['thumb.01.' + hand + '.001'] = [5, -20, -10]

        elif Tshape[0] == 'L' and Tshape[1] == '=':
            handShapeParams['thumb.01.' + hand + '.001'] = [15, 20, 5]
        elif Tshape[0] == 'L' and Tshape[1] == '<':
            handShapeParams['thumb.01.' + hand + '.001'] = [-35, 20, -10]

    elif hand == 'R':
        if Tshape[0] == 'U' and Tshape[1] == '=':
            handShapeParams['thumb.01.' + hand + '.001'] = [-10, -25, 0]
        elif Tshape[0] == 'U' and Tshape[1] == '<':
            handShapeParams['thumb.01.' + hand + '.001'] = [10, -25, 0]

        elif Tshape[0] == 'O' and Tshape[1] == '=':
            handShapeParams['thumb.01.' + hand + '.001'] = [-45, -20, 30]
        elif Tshape[0] == 'O' and Tshape[1] == '<':
            handShapeParams['thumb.01.' + hand + '.001'] = [-5, -20, 50]

        elif Tshape[0] == 'L' and Tshape[1] == '=':
            handShapeParams['thumb.01.' + hand + '.001'] = [-12, 20, -5]
        elif Tshape[0] == 'L' and Tshape[1] == '<':
            handShapeParams['thumb.01.' + hand + '.001'] = [30, 20, 10]

    return handShapeParams

## Start Script
if __name__ == '__main__':
    # Read parameters from command line needed for modifying shape
    argv = sys.argv
    codepath = argv[-5]
    hand = argv[-4]
    #print('DINOSAUR RAWR!')
    #print('-------------------------')
    #print(codepath)
    #print(hand)
    colorCode = (float(argv[-3]), float(argv[-2]), float(argv[-1]))
    
    # Read handshape coding and parse into thumb/fingers
    with open(os.path.join(codepath, 'handCode.txt'), 'r', encoding='utf-8') as inFile:
        code = inFile.read()
        parseCode = re.split('\]\d\[+', code[1:])
        [armShape, thumbShape, thumbFingerContact, indexShape, middleShape, ringShape, pinkyShape] = parseCode[:]

    #print(thumbShape)
    #print(thumbFingerContact)
    #print(indexShape)
    #print(middleShape)
    # Set hand & generate degrees of rotation, adduction & flexion
    # with open(os.path.join(os.getcwd(),'debug.txt'), 'w') as outf:
    if True:
        handShapeParams = OrderedDict()
        handShapeParams = translate_finger_code_to_degrees('index', hand, indexShape, handShapeParams)
        handShapeParams = translate_finger_code_to_degrees('middle', hand, middleShape, handShapeParams)
        handShapeParams = translate_finger_code_to_degrees('ring', hand, ringShape, handShapeParams)
        handShapeParams = translate_finger_code_to_degrees('pinky', hand, pinkyShape, handShapeParams)
        handShapeParams = translate_thumb_code_to_degrees(hand, thumbShape, handShapeParams)

        #Write to debugging file
        #outf.write(str(handShapeParams) + '\r\n')

        # Enter pose mode in blender
        bpy.ops.object.posemode_toggle()

        # deactivate current bone selected
        if not bpy.context.active_pose_bone == None:
            #print("Bone selected: " + str(bpy.context.active_pose_bone.name))
            deactThisBone = bpy.context.active_pose_bone.name
            deactThisBone = bpy.data.objects["Armature"].pose.bones[deactThisBone].bone
            deactThisBone.select = False

        #Cycle through finger bones in handShapeParams to modify the hand model:
        for strBone, param in handShapeParams.items():
            #Ensure all bones deactivated
            if bpy.context.active_pose_bone is not None:
                deactThisBone = bpy.context.active_pose_bone.name
                deactThisBone = bpy.data.objects["Armature"].pose.bones[deactThisBone].bone
                deactThisBone.select = False

            actThisBone = bpy.data.objects["Armature"].pose.bones[strBone].bone
            actThisBone.select = True

            addVDegree = param[0]
            rotVDegree = param[1]
            eleVDegree = param[2]
            eleVRadian = (eleVDegree/360)*2*pi
            addVRadian = (addVDegree/360)*2*pi
            rotVRadian = (rotVDegree/360)*2*pi

            #Apply transformations
            # Flexion/Extension occurs by moving joints about the y-axis
            bpy.ops.transform.rotate(value = eleVRadian, constraint_axis=(False, True, False))
            # Rotation of joints to reflect how natural hands adduct by moving joints about the x-axis
            bpy.ops.transform.rotate(value=rotVRadian, axis = (True, False, False))
            # Adduction of fingers occurs by moving the proximal joint (e.g. finger_index.01.L) about the z-axis
            bpy.ops.transform.rotate(value=addVRadian, axis = (False, False, True))

            #Deactivate bone
            deactThisBone = actThisBone
            deactThisBone.select = False

        # set color of hand - should create predefined colors
        if hand == 'R':
        	bpy.data.objects['Cube.000'].active_material.diffuse_color = colorCode
        elif hand == 'L':
        	bpy.data.objects['Cube.005'].active_material.diffuse_color = colorCode

        bpy.ops.object.posemode_toggle()
        print(codepath)
        
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(codepath,'handImage.blend'), copy=True)
    # Now use world matrix location to do thumb-finger contact
    """
    outf.write(thumbFingerContact)
    thumbBaseBone = 'thumb.01.' + hand + '.001'
    thumbEndBone = 'thumb.03.' + hand
    fingBone = 'finger_ring.03.' + hand

    thumbMat = bpy.data.objects["Armature"].pose.bones[thumbBaseBone].matrix
    thumbLoc, thumbRot, thumbSca = bpy.data.objects["Armature"].pose.bones[thumbBaseBone].matrix.decompose()
    thumbEndLoc, thumbEndRot, thumbEndSca = bpy.data.objects["Armature"].pose.bones[thumbEndBone].matrix.decompose()
    fingMat = bpy.data.objects["Armature"].pose.bones[fingBone].matrix
    fingLoc, fingRot, fingSca = bpy.data.objects["Armature"].pose.bones[fingBone].matrix.decompose()

    thumbLocMat = mathutils.Matrix.Translation(thumbLoc)
    thumbRotMat = thumbRot.to_matrix()

    # Manually set new thumb parameters
    manRot = deepcopy(thumbRot)
    if hand is 'L':
        manRot.x = 0.9
        manRot.y = -0.33
        manRot.z = -0.26
        manRot.w = -0.5
    else:
        manRot.x = 0
        manRot.y = 0
        manRot.z = 0
        manRot.w = 0

    manRotMat = manRot.to_matrix()
    # Apply manual rotation values to thumb matrix
    newThumbMat = deepcopy(thumbMat)
    for ii in range(3):
        for jj in range(3):
            newThumbMat[ii][jj] = manRotMat[ii][jj]

    bpy.data.objects["Armature"].pose.bones[thumbBaseBone].matrix = newThumbMat
    # Exit pose mode
    bpy.ops.object.posemode_toggle()

bpy.ops.wm.save_as_mainfile(filepath="C:/Users/Michael/Desktop/testOut2.blend", copy=True)
"""
"""
List of Bones: 	['shoulder.R', 'upper_arm.R', 'forearm.R', 'forearm.R.003', 'hand.R', 'hand.L', 
                    'palm.01.L.001', 'palm.01.L', 'palm.02.L.001', 'palm.02.L', 'palm.03.L.001', 'palm.03.L', 'palm.04.L.001', 'palm.04.L',
                    'thumb.01.L.001', 'thumb.01.L', 'thumb.02.L', 'thumb.03.L',
                    'finger_index.01.L', 'finger_index.02.L', 'finger_index.03.L',
                    'finger_middle.01.L', 'finger_middle.02.L', 'finger_middle.03.L',
                    'finger_ring.01.L', 'finger_ring.02.L', 'finger_ring.03.L',
                    'finger_pinky.01.L', 'finger_pinky.02.L', 'finger_pinky.03.L',

                    'palm.01.R.001', 'palm.01.R', 'palm.02.R.001', 'palm.02.R', 'palm.03.R.001', 'palm.03.R', 'palm.04.R.001', 'palm.04.R',
                    'thumb.01.R.001', 'thumb.01.R', 'thumb.02.R', 'thumb.03.R',
                    'finger_index.01.R', 'finger_index.02.R', 'finger_index.03.R',
                    'finger_middle.01.R', 'finger_middle.02.R', 'finger_middle.03.R',
                    'finger_ring.01.R', 'finger_ring.02.R', 'finger_ring.03.R',
                    'finger_pinky.01.R', 'finger_pinky.02.R', 'finger_pinky.03.R']
"""

# if __name__ ==  '__main__':
# 	makeHandShape()