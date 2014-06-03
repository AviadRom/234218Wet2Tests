/***************************************************************************/
/*                                                                         */
/* 234218 Data DSs 1, Spring 2014                                          */
/*                                                                         */
/* Homework : Wet 2                                                        */
/*                                                                         */
/***************************************************************************/

/***************************************************************************/
/*                                                                         */
/* File Name : main2.cpp                                                   */
/*                                                                         */
/* Holds the "int main()" function and the parser of the shell's           */
/* command line.                                                           */
/***************************************************************************/


#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include "library2.h"
#include <cstring>

using namespace std;

#ifdef __cplusplus
extern "C" {
#endif




/* The command's strings */
typedef enum {
  NONE_CMD = -2,
  COMMENT_CMD = -1,
  INIT_CMD = 0,
  VOTE_CMD = 1,
  SIGNAGREEMENT_CMD = 2,
  CAMPLEADER_CMD = 3,
  CURRENTRANKING_CMD = 4,
  QUIT_CMD = 5
} commandType;



static const int   numActions   = 6;
static const char *commandStr[] = {
  "Init",
  "Vote",
  "SignAgreement",
  "CampLeader",
  "CurrentRanking",
  "Quit"
};


static const char* ReturnValToStr(int val) {
	switch (val) {
		case (SUCCESS):          return "Success";
		case (FAILURE):          return "Failure";
		case (ALLOCATION_ERROR): return "Allocation_error";
		case (INVALID_INPUT):    return "Invalid_input";
		default:                 return "";
	}
}
	





/* we assume maximum string size is not longer than 256  */
#define MAX_STRING_INPUT_SIZE (255)
#define MAX_BUFFER_SIZE       (255)

#define StrCmp(Src1,Src2) ( strncmp((Src1),(Src2),strlen(Src1)) == 0 )

typedef enum {error_free, error} errorType;
static errorType parser(const char* const command);



#define ValidateRead(read_parameters,required_parameters,ErrorString) \
if ( (read_parameters)!=(required_parameters) ) { printf(ErrorString); return error; }


static bool isInit = false;


/* Print an array */
string PrintIntArray(const int* arr, int size) {
	char buffer[MAX_BUFFER_SIZE];
	string str = "";

	for (int i=0; i < size; i++) {
		sprintf(buffer,"%d",arr[i]);
		str += string(buffer) + ((i == (size - 1)) ? "" : ",");
	}
	return str.c_str();
}




/***************************************************************************/
/* main                                                                    */
/***************************************************************************/

int main(int argc, const char**argv) {
  char buffer[MAX_STRING_INPUT_SIZE];
  // Reading commands
  while ( fgets(buffer, MAX_STRING_INPUT_SIZE, stdin) != NULL ) {
    fflush(stdout); 
    if ( parser(buffer) == error )
      break;
    fflush(stdout);
  };
  return 0;
};

/***************************************************************************/
/* Command Checker                                                         */
/***************************************************************************/

static commandType CheckCommand(const char* const command, const char** const command_arg) {
  if ( command == NULL || strlen(command) == 0 || StrCmp("\n", command) )
    return(NONE_CMD);
  if ( StrCmp("#", command) ) {
    if (strlen(command) > 1)
      printf("%s", command);
    return(COMMENT_CMD);
  };
  for (int index=0; index < numActions; index++) {
    if ( StrCmp(commandStr[index], command) ) {
      *command_arg = command + strlen(commandStr[index]) + 1;
      return((commandType)index);
    };
  };
  return(NONE_CMD);
};

/***************************************************************************/
/* Commands Functions                                                      */
/***************************************************************************/

static errorType OnInit(void** DS, const char* const command);
static errorType OnVote(void* DS, const char* const command);
static errorType OnSignAgreement(void* DS, const char* const command);
static errorType OnCampLeader(void* DS, const char* const command);
static errorType OnCurrentRanking(void* DS, const char* const command);
static errorType OnQuit(void** DS, const char* const command);




/***************************************************************************/
/* Parser                                                                  */
/***************************************************************************/

static errorType parser(const char* const command) { 
  static void *DS = NULL; /* The general data structure */
  const char* command_args = NULL;
  errorType rtn_val = error;

  commandType command_val = CheckCommand(command, &command_args);
 
  switch (command_val) {

	case (INIT_CMD):                   rtn_val = OnInit(&DS, command_args);	break;
	case (VOTE_CMD):                   rtn_val = OnVote(DS, command_args);	break;
	case (SIGNAGREEMENT_CMD):          rtn_val = OnSignAgreement(DS, command_args);	break;
	case (CAMPLEADER_CMD):             rtn_val = OnCampLeader(DS, command_args);	break;
	case (CURRENTRANKING_CMD):         rtn_val = OnCurrentRanking(DS, command_args);	break;
	case (QUIT_CMD):                   rtn_val = OnQuit(&DS, command_args);	break;
	
	case (COMMENT_CMD):                rtn_val = error_free;	break;
	case (NONE_CMD):                   rtn_val = error;	break;
	default: assert(false);
  };
  return(rtn_val);
};



int INIT_n;


/***************************************************************************/
/* OnInit                                                                  */
/***************************************************************************/
static errorType OnInit(void** DS, const char* const command) {
	if(isInit) {
		printf("Init was already called.\n");
		return(error_free);
	};
	isInit = true;

	ValidateRead( sscanf(command, "%d" ,&INIT_n), 1, "Init failed.\n" );
		
	*DS = Init(INIT_n);
	if( *DS == NULL ) {
		printf("Init failed.\n");
		return(error);
	};
	printf("Init done.\n");

	return error_free;
}


/***************************************************************************/
/* OnVote                                                                  */
/***************************************************************************/
static errorType OnVote(void* DS, const char* const command) {
	int voterID;
	int candidate;
	ValidateRead( sscanf(command, "%d %d",&voterID,&candidate), 2, "Vote failed.\n" );
	StatusType res = Vote(DS,voterID,candidate);
	
	printf("Vote: %s\n", ReturnValToStr(res));
	
	return error_free;
}


/***************************************************************************/
/* OnSignAgreement                                                         */
/***************************************************************************/
static errorType OnSignAgreement(void* DS, const char* const command) {
	int candidate1;
	int candidate2;
	ValidateRead( sscanf(command, "%d %d",&candidate1,&candidate2), 2, "SignAgreement failed.\n" );
	StatusType res = SignAgreement(DS,candidate1,candidate2);
	
	printf("SignAgreement: %s\n", ReturnValToStr(res));
	
	return error_free;
}


/***************************************************************************/
/* OnCampLeader                                                            */
/***************************************************************************/
static errorType OnCampLeader(void* DS, const char* const command) {
	int candidate;
	ValidateRead( sscanf(command, "%d",&candidate), 1, "CampLeader failed.\n" );
	int	leader;
	StatusType res = CampLeader(DS,candidate,&leader);
	
	if (res != SUCCESS) {
		printf("CampLeader: %s\n",ReturnValToStr(res));
	}
	else {
		printf("CampLeader: %s %d\n", ReturnValToStr(res),leader);
	}

	return error_free;
}


/***************************************************************************/
/* OnCurrentRanking                                                        */
/***************************************************************************/
static errorType OnCurrentRanking(void* DS, const char* const command) {
	ValidateRead( sscanf(command, " "), 0, "CurrentRanking failed.\n" );
	
	int results[INIT_n][2];
	StatusType res = CurrentRanking(DS, results);

	if (res != SUCCESS) {
		printf("CurrentRanking: %s\n",ReturnValToStr(res));
	}
	else {
		printf("CurrentRanking: %s, ", ReturnValToStr(res));
		for (int i=0; i < INIT_n; i++) {
			printf("(%d,%d)", results[i][0], results[i][1]);
			if (i < (INIT_n - 1)) {
				printf(",");
			}
		}
		printf("\n");
	}

	return error_free;
}


/***************************************************************************/
/* OnQuit                                                                  */
/***************************************************************************/
static errorType OnQuit(void** DS, const char* const command) {
	Quit(DS);
	if( *DS != NULL ) {
		printf("Quit failed.\n");
		return(error);
	};
	isInit = false;
	printf("Quit done.\n");

	return error_free;
}




#ifdef __cplusplus
}
#endif


