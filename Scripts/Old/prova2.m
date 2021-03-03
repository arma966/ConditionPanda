clc
clear all
close all

m = 1e6;
sigma_est = 20;
mu_est = 50*rand(m,1)+200;
Pf = sort(cdf('norm',190,mu_est,sigma_est));
PDF = hist(Pf,50)/(m*max(Pf)/50);
%%
x = linspace(0,max(Pf),50);
plot(x,PDF);
Pf_mean=mean(Pf);
Pf_90=Pf(90000);