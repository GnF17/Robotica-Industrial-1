import math 
import numpy as np

L1 = 10
L2 = 90
L3 = 90

Theta1 = 0
Theta2 = 50
Theta3 = -45

def calc_x(theta1, theta2, theta3):
    return math.cos(theta1) * (L2 * math.cos(theta2) + L3 * math.cos(theta2 + theta3))
def calc_y(theta1, theta2, theta3):
    return math.sin(theta1) * (L2 * math.cos(theta2) + L3 * math.cos(theta2 + theta3))
def calc_z(theta1, theta2, theta3):
    return L1 + L2 * math.sin(theta2) + L3 * math.sin(theta2 + theta3)

def jacobian(theta1, theta2, theta3):
    dxdt1 = -math.sin(theta1) * (L2 * math.cos(theta2) + L3 * math.cos(theta2 + theta3)) 
    dxdt2 = -math.cos(theta1) * (L2 * math.sin(theta2) + L3 * math.sin(theta2 + theta3))
    dxdt3 = -math.cos(theta1) * L3 * math.sin(theta2 + theta3)
    dydt1 = math.cos(theta1) * (L2 * math.cos(theta2) + L3 * math.cos(theta2 + theta3))
    dydt2 = -math.sin(theta1) * (L2 * math.sin(theta2) + L3 * math.sin(theta2 + theta3))
    dydt3 = -math.sin(theta1) * L3 * math.sin(theta2 + theta3)
    dzdt1 = 0
    dzdt2 = L2 * math.cos(theta2) + L3 * math.cos(theta2 + theta3)
    dzdt3 = L3 * math.cos(theta2 + theta3)

    J = np.array([[dxdt1, dxdt2, dxdt3],
                  [dydt1, dydt2, dydt3],
                  [dzdt1, dzdt2, dzdt3]], dtype=float)
    return J

def inverse_jacobian(j):
    return np.linalg.inv(j)

def iteracao(q0, X0, Xa):
    Jinv = inverse_jacobian(jacobian(q0[0], q0[1], q0[2]))

    dX = Xa - X0
    qnovo = q0 + 0.5 * (Jinv.dot(dX))
    return qnovo

def solve(theta1, theta2, theta3, xa, ya, za):
    q0 = np.array([theta1, theta2, theta3])
    X0 = np.array([calc_x(theta1, theta2, theta3), calc_y(theta1, theta2, theta3), calc_z(theta1, theta2, theta3)])
    Xa = np.array([xa, ya, za]) 
 
    while np.linalg.norm(Xa - X0) > 0.1:
        q0 = iteracao(q0, X0, Xa)
        X0 = np.array([calc_x(theta1, theta2, theta3), calc_y(theta1, theta2, theta3), calc_z(theta1, theta2, theta3)])

    return q0















