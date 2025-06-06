# Dip Strike Tools - QGIS Plugin

## CI/CD

Plugin is linted, tested, packaged and published with GitHub.

If you mean to deploy it to the [official QGIS plugins repository](https://plugins.qgis.org/), remember to set your OSGeo credentials (`OSGEO_USER_NAME` and `OSGEO_USER_PASSWORD`) as environment variables in your CI/CD tool.

### Documentation

The documentation is located in `docs` subfolder, written in Markdown using [myst-parser](https://myst-parser.readthedocs.io/), structured in two main parts, Usage and Contribution, generated using Sphinx (have a look to [the configuration file](./docs/conf.py)) and is automatically generated through the CI and published on Pages: <https://gitlab.com/CNR-IGAG/dip_strike_tools/> (see [post generation steps](#2-build-the-documentation-locally) below).

----

## Next steps post generation

### 1. Set up development environment

> Typical commands on Linux (Ubuntu).

1. If you didn't pick the `git init` option, initialize your local repository:

    ```sh
    git init
    ```

1. Follow the [embedded documentation to set up your development environment](./docs/development/environment.md) to create  virtual environment and install development dependencies.
1. Add all files to git index to prepare initial commit:

    ```sh
    git add -A
    ```

1. Run the git hooks to ensure that everything runs OK and to start developing on quality standards:

    ```sh
    # run all pre-commit hooks on all files
    pre-commit run -a
    # don't be shy, run it again until it's all grren
    ```

### 2. Adjust URL and build the documentation locally

> [!NOTE]
> Since it's very hard to determine which the final documentation URL will be, the templater does not set it up. You have to do it manually.
> The final URL should be something like this: <https://{user_org}.github.io/{project_slug}>. You can find it in Pages settings of your repository: <https://gitlab.com/CNR-IGAG/dip_strike_tools//settings/pages>.

1. Have a look to the [plugin's metadata.txt file](dip_strike_tools/metadata.txt): review it, complete it or fix it if needed (URLs, etc.)., especially the `homepage` URL which should be to your GitLab or GitHub Pages.
1. Update the base URL of custom repository in [installation doc page](./docs/usage/installation.md).
1. Change the plugin's icon stored in `dip_strike_tools/resources/images`
1. Follow the [embedded documentation to build plugin documentation locally](./docs/development/documentation.md)

### 3. Prepare your remote repository

1. If you did not yet, create a remote repository on your Git hosting platform (GitHub, GitLab, etc.)
1. Create labels listed in [labeler.yml file](.github/labeler.yml) to make PR auto-labelling work.
1. Switch the source of GitHub Pages to `GitHub Actions` in your repository settings <https://gitlab.com/CNR-IGAG/dip_strike_tools//settings/pages>
1. Add the remote repository to your local repository:

    ```sh
    git remote add origin https://gitlab.com/CNR-IGAG/dip_strike_tools/
    ```

1. Commit changes:

    ```sh
    git commit -m "init(plugin): adding first files of Dip Strike Tools" -m "generated with QGIS Plugin Templater (https://oslandia.gitlab.io/qgis/template-qgis-plugin)"
    ```

1. Push the initial commit to the remote repository:

    ```sh
    git push -u origin main
    ```

1. Create a new release following the [packaging/release guide](./docs//development/packaging.md) with the tag `0.1.0-beta1` to trigger the CI/CD pipeline and publish the plugin on the [official QGIS plugins repository](https://plugins.qgis.org/) (if you picked up the option).

----

## License

Distributed under the terms of the [`GPLv2+` license](LICENSE).
