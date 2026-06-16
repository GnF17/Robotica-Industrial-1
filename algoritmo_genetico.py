import math

theta1, theta2, x_final, y_final = input().split() #120 45 100 120
comprimento1, comprimento2 = input().split() #100 120

erro = 5 #em posição
nova_posicao = 400
iteracao = 0

while nova_posicao > erro:
    
    iteracao += 1
    d_theta1 = []
    d_theta2 = []
    distancia = []

    # t1+5, t2
    posicaoX_atual = float(comprimento1)*math.cos(math.radians(float(theta1)+5)) + float(comprimento2)*math.cos(math.radians((float(theta1)+5)+float(theta2))) #d1*cos(t1)+d2*cos(t1+t2)
    posicaoY_atual = float(comprimento1)*math.sin(math.radians(float(theta1)+5)) + float(comprimento2)*math.sin(math.radians((float(theta1)+5)+float(theta2))) #d1*sin(t1)+d2*sin(t1+t2)
    distancia.append(math.sqrt(math.pow((posicaoX_atual-float(x_final)),2)+math.pow((posicaoY_atual-float(y_final)),2))) #sqrt((xi-x)^2+(yi-y)^)
    d_theta1.append(float(theta1)+5)
    d_theta2.append(float(theta2))

    # t1-5, t2
    posicaoX_atual = float(comprimento1)*math.cos(math.radians(float(theta1)-5)) + float(comprimento2)*math.cos(math.radians((float(theta1)-5)+float(theta2))) #d1*cos(t1)+d2*cos(t1+t2)
    posicaoY_atual = float(comprimento1)*math.sin(math.radians(float(theta1)-5)) + float(comprimento2)*math.sin(math.radians((float(theta1)-5)+float(theta2))) #d1*sin(t1)+d2*sin(t1+t2)
    distancia.append(math.sqrt(math.pow((posicaoX_atual-float(x_final)),2)+math.pow((posicaoY_atual-float(y_final)),2))) #sqrt((xi-x)^2+(yi-y)^)
    d_theta1.append(float(theta1)-5)
    d_theta2.append(float(theta2))

    # t1, t2+5
    posicaoX_atual = float(comprimento1)*math.cos(math.radians(float(theta1))) + float(comprimento2)*math.cos(math.radians(float(theta1)+(float(theta2)+5))) #d1*cos(t1)+d2*cos(t1+t2)
    posicaoY_atual = float(comprimento1)*math.sin(math.radians(float(theta1))) + float(comprimento2)*math.sin(math.radians(float(theta1)+(float(theta2)+5))) #d1*sin(t1)+d2*sin(t1+t2)
    distancia.append(math.sqrt(math.pow((posicaoX_atual-float(x_final)),2)+math.pow((posicaoY_atual-float(y_final)),2))) #sqrt((xi-x)^2+(yi-y)^)
    d_theta1.append(float(theta1))
    d_theta2.append(float(theta2)+5)

    # t1, t2-5
    posicaoX_atual = float(comprimento1)*math.cos(math.radians(float(theta1))) + float(comprimento2)*math.cos(math.radians(float(theta1)+(float(theta2)-5))) #d1*cos(t1)+d2*cos(t1+t2)
    posicaoY_atual = float(comprimento1)*math.sin(math.radians(float(theta1))) + float(comprimento2)*math.sin(math.radians(float(theta1)+(float(theta2)-5))) #d1*sin(t1)+d2*sin(t1+t2)
    distancia.append(math.sqrt(math.pow((posicaoX_atual-float(x_final)),2)+math.pow((posicaoY_atual-float(y_final)),2))) #sqrt((xi-x)^2+(yi-y)^)
    d_theta1.append(float(theta1))
    d_theta2.append(float(theta2)-5)

    # t1+5, t2+5
    posicaoX_atual = float(comprimento1)*math.cos(math.radians(float(theta1)+5)) + float(comprimento2)*math.cos(math.radians((float(theta1)+5)+(float(theta2)+5))) #d1*cos(t1)+d2*cos(t1+t2)
    posicaoY_atual = float(comprimento1)*math.sin(math.radians(float(theta1)+5)) + float(comprimento2)*math.sin(math.radians((float(theta1)+5)+(float(theta2)+5))) #d1*sin(t1)+d2*sin(t1+t2)
    distancia.append(math.sqrt(math.pow((posicaoX_atual-float(x_final)),2)+math.pow((posicaoY_atual-float(y_final)),2))) #sqrt((xi-x)^2+(yi-y)^)
    d_theta1.append(float(theta1)+5)
    d_theta2.append(float(theta2)+5)

    # t1+5, t2-5
    posicaoX_atual = float(comprimento1)*math.cos(math.radians(float(theta1)+5)) + float(comprimento2)*math.cos(math.radians((float(theta1)+5)+(float(theta2)-5))) #d1*cos(t1)+d2*cos(t1+t2)
    posicaoY_atual = float(comprimento1)*math.sin(math.radians(float(theta1)+5)) + float(comprimento2)*math.sin(math.radians((float(theta1)+5)+(float(theta2)-5))) #d1*sin(t1)+d2*sin(t1+t2)
    distancia.append(math.sqrt(math.pow((posicaoX_atual-float(x_final)),2)+math.pow((posicaoY_atual-float(y_final)),2))) #sqrt((xi-x)^2+(yi-y)^)
    d_theta1.append(float(theta1)+5)
    d_theta2.append(float(theta2)-5)

    # t1-5, t2+5
    posicaoX_atual = float(comprimento1)*math.cos(math.radians(float(theta1)-5)) + float(comprimento2)*math.cos(math.radians((float(theta1)-5)+(float(theta2)+5))) #d1*cos(t1)+d2*cos(t1+t2)
    posicaoY_atual = float(comprimento1)*math.sin(math.radians(float(theta1)-5)) + float(comprimento2)*math.sin(math.radians((float(theta1)-5)+(float(theta2)+5))) #d1*sin(t1)+d2*sin(t1+t2)
    distancia.append(math.sqrt(math.pow((posicaoX_atual-float(x_final)),2)+math.pow((posicaoY_atual-float(y_final)),2))) #sqrt((xi-x)^2+(yi-y)^)
    d_theta1.append(float(theta1)-5)
    d_theta2.append(float(theta2)+5)

    # t1-5, t1-5
    posicaoX_atual = float(comprimento1)*math.cos(math.radians(float(theta1)-5)) + float(comprimento2)*math.cos(math.radians((float(theta1)-5)+(float(theta2)-5))) #d1*cos(t1)+d2*cos(t1+t2)
    posicaoY_atual = float(comprimento1)*math.sin(math.radians(float(theta1)-5)) + float(comprimento2)*math.sin(math.radians((float(theta1)-5)+(float(theta2)-5))) #d1*sin(t1)+d2*sin(t1+t2)
    distancia.append(math.sqrt(math.pow((posicaoX_atual-float(x_final)),2)+math.pow((posicaoY_atual-float(y_final)),2))) #sqrt((xi-x)^2+(yi-y)^)
    d_theta1.append(float(theta1)-5)
    d_theta2.append(float(theta2)-5)

    nova_posicao = float(min(distancia))
    theta1 = float(d_theta1[distancia.index(nova_posicao)])
    theta2 = float(d_theta2[distancia.index(nova_posicao)])
    
    print(nova_posicao)

print(iteracao)
