import numpy as np
import math
import heapq

fileDict = {}

with open(
        "Antenna_pattern.txt") as f:  # accessing the antenna discrimination angle file
    for line in f:
        (key, val) = line.split(None, -1)
        fileDict[float(key)] = val  # converting the data into a dictionary to be used for calculations
        # print(d)
f.close()


# function to find the Line Of Sight distance of mobile from base station
def LOSdistance(distance):  # hypotenuse formula for calculating direct path
    x = 400
    y = distance * distance
    return (math.sqrt(x + y))


# function to calculate Line Of Sight propagation loss for each position of the mobile
def PropLoss(distance):
    D = LOSdistance(distance)
    D = D / 1000
    ruralCorr_a = 9.8243
    mobileHt_a = (1.1 * math.log10(860) - 0.7) * 1.5 - (1.56 * math.log10(860) - 0.8)
    propagationLoss_a =  69.55 + (26.16 * math.log10(860)) - (13.82 * math.log10(50)) + (
    (44.9 - (6.55 * math.log10(50))) * math.log10(D)) - mobileHt_a - ruralCorr_a

    ruralCorr_b = 9.8393
    mobileHt_b = (1.1 * math.log10(865) - 0.7) * 1.5 - (1.56 * math.log10(865) - 0.8)
    propagationLoss_b = 69.55 + (26.16 * math.log10(865)) - (13.82 * math.log10(50)) + (
    (44.9 - (6.55 * math.log10(50))) * math.log10(D)) - mobileHt_b - ruralCorr_b

    return [float(propagationLoss_a), float(propagationLoss_b)]


# function to calculate the EIRP based on angle made by the mobile position with the 2 base station sectors
def Eirp(distance):
    x = 20
    y = abs(distance - 3000)
    ang = math.degrees(math.asin(y/math.sqrt(x**2+y**2)))
    # alpha=90
    # beta=30

    if (distance > 3000):
        ang1 = 90 - ang
        ang2 = 30 + ang
    else:
        ang1 = 90 + ang
        ang2 = abs(30 - ang)
    ang1 = (round(ang1, 0))
    ang2 = (round(ang2, 0))

    for x in fileDict:
        if ang1 == x:
            eirpA = float(fileDict[x])
        if ang2 == x:
            eirpB = float(fileDict[x])
    return ([eirpA, eirpB])


# function to calculate shadowing factor at each position of the mobile
def shadowing(distance):
    shadow = np.random.normal(0, 2, 600)
    d1 = 0
    d2 = 10
    if (d2 <= 6000):
        for d in shadow:
            if d1 < distance and distance <= d2:
                return (d)
            else:
                d1 = d2
                d2 += 10


EIRPbs = 56  # EIRP of the basestation


# function to calculate RSL from each sector at a given distance
def RSLsectorA(distance):
    EIRP = (Eirp(distance)[0])
    # print(EIRP)
    PropagationLoss = (PropLoss(distance)[0])
    # print(PropagationLoss)
    fade = np.random.rayleigh(1, 10)
    fading = math.log10(heapq.nlargest(2, fade)[-1])
    # print(fading)
    shadowing_factor = shadowing(distance)
    RSL = EIRPbs - EIRP - PropagationLoss + shadowing_factor + fading
    return (RSL)


def RSLsectorB(distance):
    EIRP = (Eirp(distance)[1])
    PropagationLoss = (PropLoss(distance)[1])
    fade = np.random.rayleigh(1, 10)
    fading = math.log10(heapq.nlargest(2, fade)[-1])
    shadowing_factor = shadowing(distance)
    RSL = EIRPbs - EIRP - PropagationLoss + shadowing_factor + fading
    return (RSL)


HOm = 3
countA = 0
countB = 0
activeCalls_A = [0] * 160
callTimesA = [0] * 160
dA = [2] * 160
activeCalls_B = [0] * 160
callTimesB = [0] * 160
dB = [2] * 160
RSLthresh = -102
callsDropped_signalA = 0
callsDropped_signalB = 0
callsBlocked_capacityA = 0
callsBlocked_capacityB = 0
callsDropped_capacityA = 0
callsDropped_capacityB = 0
activeCallsCount = 0
failedCall = 0
callAttempts = 0
successfulCalls_A = 0
successfulCalls_B = 0
HOattemptAtoB = 0
HOattemptBtoA = 0
HO_A = 0
HO_B = 0
HOfailAtoB = 0
HOfailBtoA = 0
N_a = 15
N_b = 15
flag = ''

Users = np.random.uniform(0, 6000, 160)  # uniformly generatd users over a road of given length

for t in range(3600):  # simulating for 6 hours = 21600 seconds
    for i in range(len(Users)):
        if (activeCalls_A[i] == 0 and activeCalls_B[i] == 0):  # if there is no active call

            callReq = np.random.random()  # random condition to check if call request made
            p = 5.55 * math.pow(10, -4)

            if callReq < p:
                # No call request made
                continue  # go to next user

            else:  # call request made
                callAttempts += 1  # parameter b: number of call attempts
                call_length = np.random.exponential(180,
                                                    None)  # duration of the attempted call as an exponential distribution
                direction = np.random.randint(0, 2)  # to check if going north or south

                secA = RSLsectorA(Users[i])
                secB = RSLsectorB(Users[i])
                if secA > secB:  # determining the sector with the highest RSL at a given position
                    RSLserver = secA
                    flag = 'a'
                else:
                    RSLserver = secB
                    flag = 'b'

                if (RSLserver < RSLthresh):
                    failedCall += 1
                    if flag == 'a':
                        callsDropped_signalA += 1  # parameter f

                    else:
                        callsDropped_signalB += 1


                else:  # RSLserver>=RSLthresh
                    if flag == 'a':
                        # print("Serving sector = A with RSL = ",RSLserver)
                        if N_a == 0:  # no available channels
                            callsBlocked_capacityA += 1
                            if secB >= RSLthresh:
                                if N_b > 0 and N_b <= 15:
                                    N_b -= 1  # counter for available channels in sector B
                                    activeCalls_B[i] = Users[i]
                                    dB[i] = direction
                                    callTimesB[i] = call_length
                                    # print(activeCalls_B)

                                else:
                                    callsDropped_capacityA += 1
                                    continue
                        elif N_a > 0 and N_a <= 15:  # channels available
                            activeCalls_A[i] = Users[i]
                            dA[i] = direction
                            callTimesA[i] = call_length
                            # print("A",activeCalls_A)
                            N_a -= 1  # counter for available channels in sector A
                    else:
                        # print("Serving sector = B with RSL = ",RSLserver)
                        if N_b == 0:  # no available channels
                            callsBlocked_capacityB += 1
                            if secA >= RSLthresh:
                                if N_a > 0 and N_a <= 15:
                                    N_a -= 1
                                    activeCalls_A[i] = Users[i]
                                    dA[i] = direction
                                    callTimesA[i] = call_length
                                    # print("A",activeCalls_A)
                                else:
                                    callsDropped_capacityB += 1
                                    continue
                        elif N_b > 0 and N_b <= 15:
                            activeCalls_B[i] = Users[i]
                            dB[i] = direction
                            callTimesB[i] = call_length
                            # print("B",activeCalls_B)
                            N_b -= 1

        elif activeCalls_A[i] != 0:
            if dA[i] == 1:  # direction : North
                activeCalls_A[i] += 15
            elif dA[i] == 0:  # direction : South
                activeCalls_A[i] -= 15
            callTimesA[i] -= 1  # updating call timer

            if callTimesA[i] == 0:  # no time left on the call
                successfulCalls_A += 1  # successful call on this sector because call timer ran out
                activeCalls_A[i] = 0  # completion of a call- not active anymore
                N_a += 1  # freeing a channel
                continue  # done with this user

            if activeCalls_A[i] > 6000 or activeCalls_A[i] < 0:  # if mobile moved beyond the road
                successfulCalls_A += 1  # successful call on this sector coz mobile moves beyond the road
                N_a += 1  # freeing a channel
                activeCalls_A[i] = 0  # no more an active call
                continue  # done with this user

            RSLserver = RSLsectorA(activeCalls_A[i])  # RSL server at new location
            RSLother = RSLsectorB(activeCalls_A[i])
            if RSLserver < RSLthresh:
                callsDropped_signalA += 1  # call dropped due to low signal strength of serving sector
                activeCalls_A[i] = 0  # call no more active
                N_a += 1  # freeing channel
                continue  # next user
            elif RSLother > (RSLserver + HOm):
                HOattemptAtoB += 1
                if N_b > 0:  # channel available in the other sector
                    # successful handoff from A to B. Update active calls-
                    activeCalls_B[i] = activeCalls_A[i]
                    activeCalls_A[i] = 0
                    HO_A += 1  # successfull HO count
                    RSLserver = RSLother  # new serving sector
                    N_a += 1  # channel freed in old server
                    N_b -= 1  # channel used in new server
                else:
                    # handoff failure from A to B
                    # call continues on A
                    HOfailAtoB += 1  # failed HO count
                    continue
            if (activeCalls_A[i] != 0):
                countA += 1
            '''print(activeCalls_A)
            print(dA)
            print(callTimesA)#call continues in original sector'''
        elif activeCalls_B[i] != 0:
            countB += 1
            if dB[i] == 1:  # direction : North
                activeCalls_B[i] += 15
            else:  # direction : South
                activeCalls_B[i] -= 15
            callTimesB[i] -= 1  # updating call timer

            if callTimesB[i] == 0:  # no time left on the call
                successfulCalls_B += 1  # successful call on this sector because call timer ran out
                activeCalls_B[i] = 0  # completion of a call- not active anymore
                countB -= 1
                N_b += 1  # freeing a channel
                continue  # done with this user

            if activeCalls_B[i] > 6000 or activeCalls_B[i] < 0:  # if mobile moved beyond the road
                successfulCalls_B += 1  # successful call on this sector coz mobile moves beyond the road
                N_b += 1  # freeing a channel
                activeCalls_B[i] = 0  # no more an active call
                countB -= 1
                continue  # done with this user

            RSLserver = RSLsectorA(activeCalls_B[i])  # RSL server at new location
            RSLother = RSLsectorB(activeCalls_B[i])
            if RSLserver < RSLthresh:
                callsDropped_signalB += 1  # call dropped due to low signal strength of serving sector
                activeCalls_B[i] = 0  # call no more active
                countB -= 1
                N_b += 1  # freeing channel
                continue  # next user
            elif RSLother > (RSLserver + HOm):
                HOattemptBtoA += 1
                if N_a > 0:  # channel available in the other sector
                    # successful handoff from A to B. Update active calls-
                    activeCalls_A[i] = activeCalls_B[i]
                    activeCalls_B[i] = 0
                    countB -= 1
                    HO_B += 1  # successfull HO count
                    RSLserver = RSLother  # new serving sector
                    N_b += 1  # channel freed in old server
                    N_a -= 1  # channel used in new server
                else:
                    # handoff failure from A to B
                    # call continues on A
                    HOfailBtoA += 1  # failed HO count
                    continue

print("==========================================================================")
print("Call attempts: ", callAttempts)
print("Failed Calls : ", failedCall)
print("\nSector A")
print("Calls dropped due to weak signal : ", callsDropped_signalA)
print("Calls dropped due to lack of capacity : ", callsDropped_capacityA)
print("Calls blocked due to lack of capacity : ", callsBlocked_capacityA)
print("Channels available to use : ", N_a)
print("Successful calls : ", successfulCalls_A)
print("Active calls : ", countA)
print("HandOff attempts : ", HOattemptAtoB)
print("Successful Handoffs : ", HO_A)
print("Failed Handoffs : ", HOfailAtoB)
# print("A : ", activeCalls_A)
print("\nSector B")
print("Calls dropped due to weak signal : ", callsDropped_signalB)
print("Calls dropped due to lack of capacity : ", callsDropped_capacityB)
print("Calls blocked due to lack of capacity : ", callsBlocked_capacityB)
print("Channels available to use : ", N_b)
print("Successful calls : ", successfulCalls_B)
print("Active calls : ", countB)
print("HandOff attempts : ", HOattemptBtoA)
print("Successful Handoffs : ", HO_B)
print("Failed Handoffs : ", HOfailBtoA)
# print("B : ", activeCalls_B)'''
