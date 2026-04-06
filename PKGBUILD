pkgname=everydaylinuxusertools
pkgver=1.0
pkgrel=1
pkgdesc="GTK application providing everyday Linux utilities (Bluetooth control)"
arch=('any')
url="https://github.com/yourusername/everydaylinuxusertools"
license=('GPL3')
depends=('python' 'python-gobject' 'gtk3' 'polkit')
optdepends=('bluez: Bluetooth support')
source=(
    "everydaylinuxusertools.py"
    "everydaylinuxusertools.desktop"
)
sha256sums=('b91d5d20fffbfc3693d7c79840ff405b18a29c6b738b96e3b9e425bc59f31561'
            '316440be529bd0e106652e01e42336e8431ff1052ab3d666095e5b3e5c507b23')

package() {
    # Install main script
    install -Dm755 everydaylinuxusertools.py \
        "$pkgdir/usr/bin/everydaylinuxusertools"

    # Install desktop file
    install -Dm644 everydaylinuxusertools.desktop \
        "$pkgdir/usr/share/applications/everydaylinuxusertools.desktop"
}
