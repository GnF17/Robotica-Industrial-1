syms theta1
syms theta2
syms theta3
syms X
syms Z
syms L1
syms L2

A10 = [cos(theta1), 0, sin(theta1), X*cos(theta1); sin(theta1), 0, -cos(theta1), X*sin(theta1); 0, 1, 0 , Z; 0 , 0, 0, 1];



A21 = [cos(theta2), -sin(theta2), 0, L1 * cos(theta2); sin(theta2), cos(theta2), 0, L1*sin(theta2);0,0,1,0;0,0,0,1];

A32 = [cos(theta3), -sin(theta3), 0, L2*cos(theta3);sin(theta3), cos(theta3),0,L2*sin(theta3);0,0,1,0;0,0,0,1];


H_cru = A10 * A21 * A32;
H = simplify(H_cru);
pretty(H)

x = H(1,4);
y = H(2,4);
z = H(3,4);

dx_dt1 = diff(x, theta1);
dx_dt2 = diff(x, theta2);
dx_dt3 = diff(x, theta3);
dy_dt1 = diff(y, theta1);
dy_dt2 = diff(y, theta2);
dy_dt3 = diff(y, theta3);
dz_dt1 = diff(z, theta1);
dz_dt2 = diff(z, theta2);
dz_dt3 = diff(z, theta3);

J = [dx_dt1, dx_dt2, dx_dt3; dy_dt1, dy_dt2, dy_dt3; dz_dt1, dz_dt2, dz_dt3];
pretty(J)

J_inv = simplify(inv(J));
pretty(J_inv)