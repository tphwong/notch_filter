# moving away from Ann Arbor at 70mph
clear
wavelength=299800000/91700000   # wavelength of 91.7MHz in meters
distance(1)=33829.8             # distance from MOBIS to 91.7MHz radio tower in meters
speed=31.3                      # distance traveled converted to meters per second

loss_sec(1)=(20*log10(4*%pi*33829.8/wavelength))-(20*log10(4*%pi*(33829.8-speed)/wavelength))
for i=2:3600
    distance(i)=distance(i-1)+speed    
    loss_sec(i)=(20*log10(4*%pi*distance(i)/wavelength))-(20*log10(4*%pi*distance(i-1)/wavelength))
end

# for i=1:60
    # loss_min(i)=0
    # for j=1:60
        # loss_min(i)=loss_min(i)+loss_sec(j*i)
    # end
# end

# loss_hr=0
# for i=1:60
    # loss_hr=loss_hr+loss_min(i)
# end

# plot((1:60)',loss_min)

check(1)=0      //attenuate when check=1, do not attenuate when check=0
num=0
for i=1:3600
    num=num+loss_sec(i)
    if num>=1 then
        num=num-1
        check(i)=1
    else
        check(i)=0
    end
end




# earth curvature caculation will be used to define max range of FM radio
wavelength=299800000/91700000   # wavelength of 91.7MHz in meters
distance(1)=33829.8             # distance from MOBIS to 91.7MHz radio tower in meters
speed=31.3                      # distance traveled converted to meters per second
height=513                      # antenna height

# wavelength=299800000/105100000   # wavelength of 105.1MHz in meters
# distance(1)=28913.2             # distance from MOBIS to 91.7MHz radio tower in meters
# speed=31.3                      # distance traveled converted to meters per second
# height=349                      # antenna height

maxdistance=4120*sqrt(height)
