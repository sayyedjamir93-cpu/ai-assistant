#include <iostream>
#include <vector>

void printFibonacci(int n) {
    if (n <= 0) return;
    long long a = 0, b = 1;
    std::cout << a;
    for (int i = 1; i < n; ++i) {
        std::cout << " -> " << b;
        long long next = a + b;
        a = b;
        b = next;
    }
    std::cout << std::endl;
}

int main() {
    std::cout << "========================================" << std::endl;
    std::cout << "     SADIE C++ FIBONACCI GENERATOR      " << std::endl;
    std::cout << "========================================" << std::endl;

    int count;
    std::cout << "Enter number of terms: ";
    if (std::cin >> count) {
        std::cout << "\nFibonacci Series (" << count << " terms):\n";
        printFibonacci(count);
    }
    return 0;
}
