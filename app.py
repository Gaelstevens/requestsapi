void sys_write(int fd, const char *buf, int len)
{
    asm volatile (
        "movl $1, %%eax \n"   // syscall write (1)
        "movl %0, %%edi \n"   // file descriptor (1 = stdout)
        "movl %1, %%esi \n"   // buffer address
        "movl %2, %%edx \n"   // buffer length
        "syscall"
        :
        : "g"(fd), "g"(buf), "g"(len)
        : "%eax", "%edi", "%esi", "%edx"
    );
}

int ft_strlen(const char *str)
{
    int len = 0;
    while (str[len])
        len++;
    return len;
}

void ft_putstr(const char *str)
{
    sys_write(1, str, ft_strlen(str));
}

void ft_putchar(char c)
{
    sys_write(1, &c, 1);
}

// Fonction pour convertir un nombre en chaîne de caractères
void ft_itoa(int num, char *str)
{
    int i = 0, is_neg = 0;
    if (num == 0)
    {
        str[i++] = '0';
    }
    if (num < 0)
    {
        is_neg = 1;
        num = -num;
    }
    while (num)
    {
        str[i++] = (num % 10) + '0';
        num /= 10;
    }
    if (is_neg)
        str[i++] = '-';
    str[i] = '\0';

    // Inverser la chaîne
    for (int j = 0; j < i / 2; j++)
    {
        char temp = str[j];
        str[j] = str[i - j - 1];
        str[i - j - 1] = temp;
    }
}

// Fonction de base printf qui ne gère que %s, %c et %d
void ft_printf(const char *format, ...)
{
    char **args = (char **)(&format) + 1;
    while (*format)
    {
        if (*format == '%' && *(format + 1))
        {
            format++;
            if (*format == 's') // Gestion des chaînes de caractères
            {
                char *str = *(args++);
                ft_putstr(str);
            }
            else if (*format == 'c') // Gestion des caractères
            {
                char c = *(char *)(args++);
                ft_putchar(c);
            }
            else if (*format == 'd') // Gestion des entiers
            {
                int num = *(int *)(args++);
                char buffer[12];
                ft_itoa(num, buffer);
                ft_putstr(buffer);
            }
        }
        else
        {
            ft_putchar(*format);
        }
        format++;
    }
}

// Fonction de test
int main()
{
    ft_printf("Hello %s!\n", "World");
    ft_printf("Number: %d\n", 123);
    ft_printf("Char: %c\n", 'A');
    return 0;
}