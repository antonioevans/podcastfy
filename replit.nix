{ pkgs }: {
    deps = [
        pkgs.python39
        pkgs.python39Packages.pip
        pkgs.ffmpeg
        pkgs.imagemagick
        pkgs.nodejs
        pkgs.nodePackages.typescript
        pkgs.nodePackages.typescript-language-server
    ];
    env = {
        PYTHONBIN = "${pkgs.python39}/bin/python3.9";
        LANG = "en_US.UTF-8";
        PYTHONIOENCODING = "utf-8";
    };
}
