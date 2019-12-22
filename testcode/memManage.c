int main(void)
{
  char *address1, *address2, *address3, *address4, *address5;

  address1 = malloc(111);
  address2 = malloc(222);
  address3 = malloc(333);
  free(address2);
  address4 = malloc(444);
  address5 = malloc(555);
}