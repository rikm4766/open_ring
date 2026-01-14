#include<stdio.h>
#include"rf_model.h"
int m;

int main(){
    double input[4]={5.1, 3.5, 1.4, 0.2};

    double output[4];


    score_rf(input,output);



    double max=output[0];

    
    for(int i=0;i<4;i++){
        printf("%f\t",output[i]);
        if(max<output[i]){
            max=output[i];
            m=i;
        }
    }
    printf("\n");
    printf("OUTPUT is %d\n",m);

    return 0;
}