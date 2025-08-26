from factories.product_factory import RequestCreateProductDtoFactory


class TestProducts:
    def test_create_product(self, api_products_methods):
        data = RequestCreateProductDtoFactory.build().model_dump()  # model_dump() это замена dict(), который deprecated
        api_products_methods.create_product(data)
