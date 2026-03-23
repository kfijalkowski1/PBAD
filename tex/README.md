# WEiTI project report template

LaTeX template for project reports.

# Usage

Tested to work with `texlive-full` version `2024.20250309-1` on Debian 13.

## With VS Code

```shell
cp -r .vscode-sample .vscode
```

Install [LaTeX Workshop](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop), [LTeX](https://marketplace.visualstudio.com/items?itemName=valentjn.vscode-ltex) and Polish language for [cSpell](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker-polish). Should compile out of the box.

## With any other editor

Compile using `lualatex`:

```shell
make            # builds main.pdf
make pdf        # same as above
make clean      # removes aux files
make clean-all  # also removes main.pdf
```

# Credits

Heavily inspired by https://github.com/ArturB/WUT-Thesis and https://www.overleaf.com/latex/templates/mim-uw-bachelors-and-masters-thesis-template/zbkxgfmsbpzq
