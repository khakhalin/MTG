# The number of total comparisons between the pack and the collection
c <- 0
total <- 0
for (i in 1:3){
  for(j in 15:1){
    total <- total+j*c
    c <- c+1
  }
}
print(total)

# Total draft conditions
nc = 100 # commons
nu = 80 # uncommons
nr = 79 # rares and mythics coz I'm lazy
np = 8*3 # packs

