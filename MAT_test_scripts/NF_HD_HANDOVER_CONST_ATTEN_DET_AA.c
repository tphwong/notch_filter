/***********************************************************************************************
* Tester       : 
* Date         : 
* Test Case ID : 
* Precondition : 

* Comment      : 

***********************************************************************************************/

#include <mat.h>
#include "MASTER.c"
	
main()
{	
/*****************************************PRECONDITION*****************************************/
	//DELAY(1000); USB(0);
	//ADB_CAM(1);
	//HOME();
	
	HOME(); DELAY(1000);

/********************************************STEPS*********************************************/
	
	HD_ENGR_MODE();
	
	MAT_Process("C:\\Program Files\\Python 3.5\\python.exe C:\\Users\\abc\\Desktop\\notch_filter\\nf_handover_const_atten_Det_AA.py", 0, 1, INFINITE);
	DELAY(45000);
	
	VERIFY_IMAGE("NF_HD_FREQ_AA");
	VERIFY_IMAGE("NF_HD_STATE_MONITORING");
	DELAY(1000);
	
/****************************************POSTCONDITION*****************************************/
	HD_ENGR_MODE_BACKTRACK();
	
	//ANR_CHECK();
	//ADB_CAM(0);
}