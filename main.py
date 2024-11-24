import json
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())

with open("policy.json", "r") as f:
    policy = json.load(f)
    extensions: list[str] = policy["chromePolicies"]["ExtensionInstallAllowlist"]["value"]
    force_installed_extensions: list[str] = policy["chromePolicies"]["ExtensionInstallForcelist"]["value"]
    extensions = [i for i in extensions if i not in [i.partition(';')[0] for i in force_installed_extensions]]
    print(extensions, force_installed_extensions)
    out = []

    for ext_id in extensions:
        site = f"https://chromewebstore.google.com/detail/{ext_id}"
        driver.get(site)
        page = driver.page_source
        if "https://www.gstatic.com/chrome/webstore/images/item_not_available.png" in page:
            continue
        tmp = {
            "id": ext_id,
            "page": site,
            "name": page.partition('alt="Item logo image for ')[2].partition('"')[0],
            # "tr3nch_compatible": "No" if 'aria-label="Featured Badge"' in page else "Maybe",
            # stupid because in skivox you can install any extension anyways due to policy not in effect
            "forced": False,
            "last_updated": page.partition('Details')[2].partition('Updated')[2].partition('<div>')[2].partition('</div>')[0],
            "size": page.partition('Details')[2].partition('Size')[2].partition('<div>')[2].partition('</div>')[0],
            "rating": float(page.partition('--star-icon-size: 18px')[2].partition('</span>')[0].split('>')[-1]),
            "reviews": page.partition('/reviews')[2].partition(' rating')[0].split('>')[-1] if '/reviews' in page else -1,
            "users": int(page.partition(' users</div>')[0].split('>')[-1].replace(',', '')) if 'users</div>' in page else -1
        }

        if 'K' in tmp["reviews"]:
            tmp['reviews'] = int(float(tmp['reviews'][:-1])*1000)
        else:
            tmp['reviews'] = int(tmp['reviews'])
        if ' href="./category/themes">Theme</a>' in page:
            tmp["type"] = "theme"
            # tmp["tr3nch_compatible"] = "No"
        elif "This item can only run on ChromeOS" in page:
            tmp["type"] = "app"
            # tmp["tr3nch_compatible"] = "No"
        else:
            tmp["type"] = "extension"
        print(tmp)
        out.append(tmp)
    for i in force_installed_extensions:
        site = i.partition(";")[2]
        ext_id = i.partition(";")[0]
        if site == "https://clients2.google.com/service/update2/crx":
            site = f"https://chromewebstore.google.com/detail/{ext_id}"
            driver.get(site)
            page = driver.page_source
            if "https://www.gstatic.com/chrome/webstore/images/item_not_available.png" in page:
                continue
            tmp = {
                "id": ext_id,
                "page": site,
                "name": page.partition('alt="Item logo image for ')[2].partition('"')[0],
                # "tr3nch_compatible": "No" if 'aria-label="Featured Badge"' in page else "Maybe",
                "forced": True,
                "last_updated": page.partition('Details')[2].partition('Updated')[2].partition('<div>')[2].partition('</div>')[0],
                "size": page.partition('Details')[2].partition('Size')[2].partition('<div>')[2].partition('</div>')[0],
                "rating": float(page.partition('--star-icon-size: 18px')[2].partition('</span>')[0].split('>')[-1]),
                "reviews": page.partition('/reviews')[2].partition(' rating')[0].split('>')[-1] if '/reviews' in page else -1,
                "users": int(page.partition(' users</div>')[0].split('>')[-1].replace(',', '')) if 'users</div>' in page else -1
            }

            if 'K' in tmp["reviews"]:
                tmp['reviews'] = int(float(tmp['reviews'][:-1]) * 1000)
            else:
                tmp['reviews'] = int(tmp['reviews'])

            if ' href="./category/themes">Theme</a>' in page:
                tmp["type"] = "theme"
                # tmp["tr3nch_compatible"] = "No"
            elif "This item can only run on ChromeOS" in page:
                tmp["type"] = "app"
                # tmp["tr3nch_compatible"] = "No"
            else:
                tmp["type"] = "extension"
            print(tmp)
        else:
            tmp = {
                "id": ext_id,
                "page": site,
                "name": "Unkown",
                # "tr3nch_compatible": "Maybe",
                "forced": True,
                "last_updated": "Unkown",
                "size": "Unkown",
                "rating": -1.0,
                "reviews": -1,
                "users": -1,
            }
            print(tmp)
        out.append(tmp)
with open("out.json", "w+") as f:
    json.dump(out, f)
