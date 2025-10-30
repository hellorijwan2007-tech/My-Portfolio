#Create an program display questin and answers of the user use list data type to store their question and answer
print("Welcome to kon banega core pati.")
print("we are() goining to ask you some question which you have to answer correctly.Note: you have only 3 attempts")
quest=["Which is the biggest animal on the world:","Iron man of nepal:","First Pm of nepal"]
ans=["Bluewhale",'Ganesh Man Singh','Bhimsen Thapa']
attempts=int((input("Enter how many times you have to try:")))
count=0
def loop(attempts):
    if  attempts> 0:
        for i in range(attempts):   # loops from 0 to n-1
            answer= quest[i]
            if(answer==ans[i]):
                print("You won")
            else:
             count= count +1
             if count>0:
                for i in range(count):
                    print("You lost 10 laks")
            

loop(attempts)
