from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import PrivateMemory
from .serializers import PrivateMemorySerializer
from .services import embed_and_save_memory


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def memory_list(request):
    """
    GET  — list all memories for the authenticated user
    POST — save a new memory (explicit save action from UI)
    """
    if request.method == "GET":
        kind = request.query_params.get("kind")
        qs = request.user.memories.all()
        if kind:
            qs = qs.filter(kind=kind)
        return Response(PrivateMemorySerializer(qs, many=True).data)

    # POST — embed and save
    serializer = PrivateMemorySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    memory = embed_and_save_memory(
        user=request.user,
        content=serializer.validated_data["content"],
        kind=serializer.validated_data.get("kind", PrivateMemory.KIND_FACT),
        source_message_id=request.data.get("source_message_id"),
    )
    return Response(PrivateMemorySerializer(memory).data, status=status.HTTP_201_CREATED)


@api_view(["DELETE", "PATCH"])
@permission_classes([IsAuthenticated])
def memory_detail(request, pk):
    """
    DELETE — remove a memory
    PATCH  — toggle pinned status
    """
    try:
        memory = request.user.memories.get(pk=pk)
    except PrivateMemory.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        memory.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # PATCH — only allow toggling pinned
    pinned = request.data.get("pinned")
    if pinned is not None:
        memory.pinned = bool(pinned)
        memory.save(update_fields=["pinned"])
    return Response(PrivateMemorySerializer(memory).data)