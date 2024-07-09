#include<stdio.h>
#include "u1.h"
#include "s1.h"
#include "s2.h"
#include "s5.h"
#include "e1.h"
#include "e2.h"
#include "e3.h"
#include "delay.h"

int main()
{
	char buf[10] = "";
	u1_led_init();
	u1_timer0_init();
	e1_led_info = e1_led_init();
	e1_tube_info = e1_tube_init();
	e2_fan_info = e2_fan_init();
	e3_curtain_info = e3_curtain_init();
	s1_key_info = s1_key_init();
	s2_illuminance_info = s2_illuminance_init();
	s2_ths_info = s2_ths_init();
	s2_imu_info = s2_imu_init();
	s5_nfc_info = s5_nfc_init();
	s2_ths_t ths_value; 
	s2_imu_t imu_value;
	
	
	while(1)
	{
		imu_value = s2_imu_value_get(s2_imu_info);
		
		sprintf(buf,"%.1f",imu_value.acc_y);
		e1_tube_str_set(e1_tube_info,buf);
		ths_value = s2_ths_value_get(s2_ths_info);
		e2_fan_speed_set(e2_fan_info,(ths_value.temp-26));
		e3_curtain_position_set(e3_curtain_info,50+imu_value.acc_y*5);
		delay_ms(100);
	}
}
int f(float temp)
		{
			int te = atoi(temp);
			
		};
