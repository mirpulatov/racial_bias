TEST_IMAGE = "tests/nopreview.png"


def test_post_form_data(client):
    res = client.post(
        "/process",
        data={
            "neural": ["1, 6"]
        },
        files={
            "first_image": (TEST_IMAGE, image),
            "second_image": (TEST_IMAGE, image),
        }
    )

    assert 200 == res.status_code
