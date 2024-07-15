from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
import os
import tempfile
from samgeo import SamGeo
import cv2


@api_view(['POST'])
def get_image(request):
    coordinates = request.data.get('coordinates')
    
    if not coordinates:
        return Response({'error': 'Coordinates not provided'}, status=400)

    try:
        north = coordinates.get('north')
        south = coordinates.get('south')
        east = coordinates.get('east')
        west = coordinates.get('west')

        if not all([north, south, east, west]):
            return Response({'error': 'Invalid coordinates'}, status=400)

        north = (north + south) / 2 + 0.01
        south = (north + south) / 2 - 0.01
        east = (east + west) / 2 + 0.01
        west = (east + west) / 2 - 0.01

        with tempfile.NamedTemporaryFile(delete=False, suffix='.tiff') as temp_file:
            image_path = temp_file.name

        samgeo = SamGeo(north=north, south=south, east=east, west=west)
        
        samgeo.download_tms_as_tiff(image_path)

        output_path = os.path.splitext(image_path)[0] + '.png'
        img = cv2.imread(image_path)
        cv2.imwrite(output_path, img)

        with open(output_path, 'rb') as image_file:
            image_data = image_file.read()
            print(image_data)
        response = HttpResponse(image_data, content_type="image/png")
        response['Content-Disposition'] = f'attachment; filename="downloaded_image.png"'
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)
        if os.path.exists(output_path):
            os.remove(output_path)
    
    return response

