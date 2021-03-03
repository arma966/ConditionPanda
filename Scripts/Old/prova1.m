x = 150:.01:350;
y=cdf('normal',x,250,25);
p=1-y(find(x==200))
plot(x,y)