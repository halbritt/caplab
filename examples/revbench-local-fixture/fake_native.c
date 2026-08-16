#include <stdio.h>
#include <string.h>

static int review(void) {
    char request[8192];
    size_t count = fread(request, 1, sizeof(request) - 1, stdin);
    if (ferror(stdin) || (!feof(stdin) && count == sizeof(request) - 1)) {
        return 2;
    }
    request[count] = '\0';

    const char *pointer = NULL;
    int defect = 0;
    if (strstr(request, "\"pointer\":\"/n\"") != NULL) {
        pointer = "/n";
        defect = strstr(request, "\"artifact\":{\"n\":0}") != NULL;
    } else if (strstr(request, "\"pointer\":\"/limits/minimum\"") != NULL) {
        pointer = "/limits/minimum";
        defect = strstr(
            request,
            "\"artifact\":{\"label\":\"b\",\"limits\":{\"minimum\":2}}"
        ) != NULL;
    } else {
        return 3;
    }

    if (defect) {
        printf(
            "{\"schema_version\":\"caplab-revbench-native-response/1\","
            "\"verdict\":\"defect\",\"anchors\":[\"%s\"]}",
            pointer
        );
    } else {
        fputs(
            "{\"schema_version\":\"caplab-revbench-native-response/1\","
            "\"verdict\":\"clean\",\"anchors\":[]}",
            stdout
        );
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "--version") == 0) {
        fputs("fake-native 1\n", stdout);
        return 0;
    }
    if (argc == 2 && strcmp(argv[1], "review") == 0) {
        return review();
    }
    return 1;
}
