//import io

function if_test(int a, int b) -> int
{
    if(a < b)
    {
        return b
    }

    return a
}

function while_test(int a, int b) -> int
{
    while(a < b)
    {
        a += 1
    }
    return a
}

function for_test(int a, int b) -> int
{
    for(int i := 0; i < 10; i += 1)
    {
        a := a + i
    }
    return a + b
}

function a(int x, int y) -> int
{
    int b := 2
    b := b * b

    for_test(10, 20)
    return x + y + 1
}
