#We can use a break statement inside a while loop to terminate the loop immediately, even if the while condition is true
i = 1
while i < 6:
  print(i)
  if i == 3:
    break
  i += 1