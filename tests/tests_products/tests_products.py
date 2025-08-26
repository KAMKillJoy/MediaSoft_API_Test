from decimal import Decimal

from factories.product_factory import RequestCreateProductDtoFactory


class TestProducts:
    def test_create_product(self, db_intest_data_cleanup, api_products_methods, db_methods):
        data = RequestCreateProductDtoFactory.build().model_dump()  # model_dump() это замена dict(), который deprecated
        db_intest_data_cleanup.append({"table": "product",
                                       "attribute": "article",
                                       "value": data["article"]})

        response = api_products_methods.create_product(data)
        assert response.status_code == 201
        assert db_methods.check_product_exists_by_article(data['article'])

        response_data = response.json()
        assert response_data['name'] == data['name']
        assert response_data['article'] == str(data['article'])
        assert response_data['category'] == data['category']
        assert response_data['price'] == data['price']
        assert response_data['qty'] == data['qty']

        db_product = db_methods.get_product_by_article(data['article'])
        assert len(db_product) == 1

        assert db_product[0]['name'] == data['name']
        assert db_product[0]['category'] == data['category']
        assert db_product[0]['price'] == Decimal(data['price']).quantize(Decimal('0.01'))
        assert db_product[0]['qty'] == data['qty']
