package com.defamation.backend.web;

import com.defamation.backend.repository.ClassificationRequestRepository;
import com.defamation.backend.web.dto.ClassificationRequestDto;
import com.defamation.backend.web.dto.PageResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.*;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/classification-requests")
@RequiredArgsConstructor
public class ClassificationRequestController {

    private final ClassificationRequestRepository repo;
    private final ObjectMapper om = new ObjectMapper();

    // GET /api/classification-requests?q=키워드&page=0&size=10
    @GetMapping
    public PageResponse<ClassificationRequestDto> list(
            @RequestParam(required = false) String q,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size
    ) {
        Pageable pageable = PageRequest.of(page, size);
        Page<ClassificationRequestDto> result = repo.search(q, pageable)
                .map(r -> ClassificationRequestDto.from(r, om));

        return PageResponse.<ClassificationRequestDto>builder()
                .items(result.getContent())
                .page(page)
                .size(size)
                .totalElements(result.getTotalElements())
                .totalPages(result.getTotalPages())
                .build();
    }
}
