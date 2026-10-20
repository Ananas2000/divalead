/* Input-driven quadratic harmonic excitation, no recording or MIDI table. */
static const double EXCITER_PARAMETERS[6]={67.520618826264212,2.4924663975397463,-0.098094062890221184,-0.00047220495128427064,-0.14699939928094624,0.03007262555945674};
typedef struct {double zr[2],zi[2],dc[2],real_pole,imag_pole,hp;} Exciter;
static void exciter_prepare(Exciter *e,double sr){
 memset(e,0,sizeof(*e));double w=2*3.14159265358979323846*EXCITER_PARAMETERS[0]/sr,r=exp(-w/(2*EXCITER_PARAMETERS[1]));e->real_pole=r*cos(w);e->imag_pole=r*sin(w);e->hp=exp(-2*3.14159265358979323846*10/sr);
}
static void exciter_process(Exciter *e,double x[2]){
 double r=hypot(e->real_pole,e->imag_pole);
 for(int c=0;c<2;c++){
  double real=e->real_pole*e->zr[c]-e->imag_pole*e->zi[c]+(1-r)*x[c],imag=e->imag_pole*e->zr[c]+e->real_pole*e->zi[c];e->zr[c]=real;e->zi[c]=imag;
  double add=2*(EXCITER_PARAMETERS[2+2*c]*(real*real-imag*imag)-EXCITER_PARAMETERS[3+2*c]*2*real*imag);e->dc[c]=e->hp*e->dc[c]+(1-e->hp)*add;x[c]+=add-e->dc[c];
 }
}
